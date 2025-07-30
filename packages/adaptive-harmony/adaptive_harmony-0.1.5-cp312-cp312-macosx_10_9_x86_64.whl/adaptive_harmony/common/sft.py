from tqdm.auto import tqdm
from adaptive_harmony import StringThread, DataSet, CosineScheduler, TrainingModel, Logger, JobNotifier
from adaptive_harmony.core.utils import async_map_batch
from adaptive_harmony.metric_logger import StdoutLogger


class SFT:

    def __init__(
        self,
        dataset: list[StringThread],
        model: TrainingModel,
        logger: Logger = StdoutLogger(),
        job_notifier: JobNotifier = JobNotifier(),
        stage_name: str = "SFT Training",
        lr: float = 1e-5,
        samples_per_batch=512,  # axel magic number: "pretty well validated across different scales"
        max_grad_norm=1.0,
    ):
        self.dataset = DataSet(dataset)
        self.lr_schedule = CosineScheduler(lr)
        self.model = model
        self.logger = logger
        self.job_notifier = job_notifier
        self.stage_name = stage_name
        self.samples_per_batch = samples_per_batch
        self.max_grad_norm = max_grad_norm

    async def run(self):
        with tqdm(total=100) as pbar:
            while self.dataset.completion_percentage() < 1.0:
                self.job_notifier.report_training_progress(
                    stage=self.stage_name,
                    tot_num_samples=len(self.dataset),
                    processed_num_samples=self.dataset.idx,
                    monitoring_link=self.logger.training_monitoring_link,
                )

                await async_map_batch(self.model.train_language_modelling, self.dataset, self.samples_per_batch)
                cp = self.dataset.completion_percentage()
                current_lr = self.lr_schedule(cp)
                pbar.update(cp * 100.0 - pbar.n)

                logs = await self.model.optim_step(current_lr, wd=0, max_grad_norm=self.max_grad_norm)
                self.logger(logs | dict(completion_percentage=cp))
