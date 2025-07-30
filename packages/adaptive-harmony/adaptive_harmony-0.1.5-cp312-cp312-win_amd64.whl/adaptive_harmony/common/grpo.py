import numpy as np
from dataclasses import dataclass

from adaptive_harmony import (
    StringThread,
    DataSet,
    CosineScheduler,
    TrainingModel,
    Logger,
    TokenizedThread,
    JobNotifier,
)
from adaptive_harmony.common.validation import run_validation
from adaptive_harmony.core.utils import async_map_batch, async_map, get_minibatches, log_args
from adaptive_harmony.metric_logger import StdoutLogger
from adaptive_harmony.scoring import Scorer


@dataclass
class Batch:
    samples: list[TokenizedThread]
    logprobs: list[list[float]]
    ref_logprobs: list[list[float]]
    advantages: list[float]
    score: float
    kl_div: list[float]
    gen_len: float


class GRPO:
    @log_args
    def __init__(
        self,
        dataset: list[StringThread],
        model: TrainingModel,
        scorer: Scorer,
        logger: Logger = StdoutLogger(),
        job_notifier: JobNotifier = JobNotifier(),
        stage_name: str = "GRPO Training",
        validation_dataset: list[StringThread] | None = None,
        validation_frequency: float = 0.2,
        max_num_grpo_steps: int | None = None,
        completions_per_sample=8,
        lr: float = 7.5e-7,
        samples_per_batch=128,
        samples_per_mini_batch=128,
        mini_epochs_per_batch=1,
        max_grad_norm=1.0,
        clip_range=0.1,
        kl_beta=0.1,
    ):
        # Core components
        self.dataset = DataSet(dataset, allow_looping=True)
        self.model = model
        self.scorer = scorer
        self.scoring_fn = scorer.score_without_metadata
        self.logger = logger
        self.job_notifier = job_notifier
        self.stage_name = stage_name
        # Validation data/params
        self.validation_dataset = validation_dataset
        self.validation_frequency = validation_frequency
        self.last_validation_percentage = -1.0  # Validation will run before training starts
        # GRPO HP's
        self.max_num_batches = max_num_grpo_steps
        self.completions_per_sample = completions_per_sample
        self.lr_schedule = CosineScheduler(lr)
        self.samples_per_batch = samples_per_batch // completions_per_sample
        self.samples_per_mini_batch = samples_per_mini_batch
        self.total_num_samples = (
            self.max_num_batches * self.samples_per_batch if self.max_num_batches else len(self.dataset)
        )
        self.max_grad_norm = max_grad_norm
        self.clip_range = clip_range
        self.kl_beta = kl_beta
        self.mini_epochs_per_batch = mini_epochs_per_batch

        self.num_batches_processed = 0

    @property
    def completion_percentage(self):
        return (
            self.dataset.completion_percentage()
            if self.max_num_batches is None
            else min(self.num_batches_processed / self.max_num_batches, 1.0)
        )

    async def gen_data(self, sample: StringThread) -> Batch:
        assert self.model_ref is not None, "Calling `gen_data` before reference model has been set"

        all_samples = await async_map(self.model.generate_tokens, [sample] * self.completions_per_sample)
        string_samples = await async_map(self.model.detokenize_thread, all_samples)
        all_scores = np.array(await async_map(self.scoring_fn, string_samples))

        advantages = all_scores - all_scores.mean()
        advantages /= advantages.std() + 1e-8

        logprobs = await async_map(self.model.logprobs_per_token, all_samples)
        ref_logprobs = await async_map(self.model_ref.logprobs_per_token, all_samples)
        kl = np.array(np.concatenate(logprobs), dtype=np.float32) - np.array(
            np.concatenate(ref_logprobs), dtype=np.float32
        )

        return Batch(
            samples=all_samples,
            logprobs=logprobs,
            ref_logprobs=ref_logprobs,
            advantages=advantages,
            score=np.mean(all_scores).item(),
            kl_div=kl.tolist(),
            gen_len=float(np.mean([sample.len_last_turn() for sample in all_samples])),
        )

    async def train_mini_batch(self, data: Batch):
        for i in range(len(data.samples)):
            await self.model.train_grpo(
                data.samples[i],
                data.logprobs[i],
                data.ref_logprobs[i],
                [data.advantages[i]] * len(data.logprobs[i]),
                self.clip_range,
                self.kl_beta,
            )

    async def run(self):
        self.model_ref = await self.model.clone_inf()

        while self.completion_percentage < 1.0:
            self.job_notifier.report_training_progress(
                stage=self.stage_name,
                tot_num_samples=self.total_num_samples,
                processed_num_samples=self.num_batches_processed * self.samples_per_batch,
                monitoring_link=self.logger.training_monitoring_link,
            )
            self.num_batches_processed += 1

            # Run validation if needed
            should_run_validation = (
                self.validation_dataset is not None
                and self.completion_percentage - self.last_validation_percentage >= self.validation_frequency
            )
            if should_run_validation:
                assert self.validation_dataset is not None, "validation_samples must be set"
                val_logs = await run_validation(self.validation_dataset, self.model, self.scoring_fn)
                val_scorer_logs = self.scorer.get_logs(clear=True)
                val_logs = {  # Join all validation logs
                    **val_logs,
                    **{"validation/completion_percentage": self.completion_percentage},
                    **{f"validation/rewards/{key}": value for key, value in val_scorer_logs.items()},
                }
                self.logger(val_logs)
                self.last_validation_percentage = self.completion_percentage

            # Generate training samples
            data = await async_map_batch(self.gen_data, self.dataset, self.samples_per_batch)
            scorer_logs = self.scorer.get_logs(clear=True)
            batch_logs = {
                **{f"rewards/{key}": value for key, value in scorer_logs.items()},
                **self.get_train_batch_logs(data),
            }

            current_lr = self.lr_schedule(self.completion_percentage)

            # Train on generated samples
            for mini_batch in get_minibatches(
                data, self.samples_per_mini_batch // self.completions_per_sample, self.mini_epochs_per_batch
            ):
                await async_map(self.train_mini_batch, mini_batch)
                optim_logs = await self.model.optim_step(current_lr, wd=0, max_grad_norm=self.max_grad_norm)
                self.logger(optim_logs | batch_logs)

        self.logger.close()

    def get_train_batch_logs(self, data: list[Batch]) -> dict:
        return {
            **dict(
                completion_percentage=self.completion_percentage,
                percentage_no_advantages=np.mean(
                    [all(advantage == batch.advantages[0] for advantage in batch.advantages) for batch in data]
                ),
                score_mean=np.mean([batch.score for batch in data]).item(),
                score_std=np.std([batch.score for batch in data]).item(),
                kl_div=np.mean(np.concatenate([batch.kl_div for batch in data])),
                advantages=np.mean(np.concatenate([batch.advantages for batch in data])),
                generation_length=np.mean([batch.gen_len for batch in data]),
                logprobs=np.mean(np.concatenate([np.concatenate(batch.logprobs) for batch in data])),
                ref_logprobs=np.mean(np.concatenate([np.concatenate(batch.ref_logprobs) for batch in data])),
            ),
            **{"training/completion_percentage": self.completion_percentage},
        }
