from adaptive_harmony import StringThread, DataSet, CosineScheduler, TrainingModel, Logger
from adaptive_harmony.core.utils import async_map_batch


class DPO:
    def __init__(
        self,
        data_set: list[tuple[StringThread, StringThread]],  # (positive_sample, negative_sample)
        model: TrainingModel,
        logger: Logger,
        lr: float = 1e-4,
        samples_per_batch=32,
        max_grad_norm=1.0,
        beta=0.1,
    ):
        self.model_ref = None
        self.dataset = DataSet(data_set)
        self.lr_schedule = CosineScheduler(lr)
        self.model = model
        self.samples_per_batch = samples_per_batch
        self.logger = logger
        self.max_grad_norm = max_grad_norm
        self.beta = beta

    async def process_sample(self, sample: tuple[StringThread, StringThread]):
        assert self.model_ref is not None, "Calling `process_sample_dpo` before reference model has been set"

        pos, neg = sample
        ref_logprobs_pos = await self.model_ref.logprobs(pos)
        ref_logprobs_neg = await self.model_ref.logprobs(neg)
        await self.model.train_dpo(pos, neg, ref_logprobs_pos, ref_logprobs_neg, self.beta)

    async def run(self):
        self.model_ref = await self.model.clone_inf()

        while self.dataset.completion_percentage() < 1.0:
            await async_map_batch(self.process_sample, self.dataset, self.samples_per_batch)
            current_lr = self.lr_schedule(self.dataset.completion_percentage())
            logs = await self.model.optim_step(current_lr, wd=0, max_grad_norm=self.max_grad_norm)
            self.logger(logs)
