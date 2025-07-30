from adaptive_harmony import HarmonyClient, get_client, JobNotifier, HarmonyJobNotifier
from adaptive_harmony.runtime.input import AdaptiveModel
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Self


class RecipeConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADAPTIVE_", cli_parse_args=True, cli_kebab_case=True)

    harmony_url: str = Field(description="url of harmony service")
    user_input_file: str | None = None
    job_id: str = "test"
    use_case: str | None = None
    api_key: str | None = None
    compute_pool: str | None = None
    num_gpus: int | None = None

    # temporary training params, should be part of the recipe input
    input_model_key: str | None = None
    output_model_key: str | None = None
    output_model_name: str | None = None


class RecipeContext:
    client: HarmonyClient
    job: JobNotifier
    model_to_train: AdaptiveModel | None
    config: RecipeConfig
    # todo: pass world size
    world_size: int = 1

    def __init__(self, client: HarmonyClient, config: RecipeConfig):
        self.client = client
        self.config = config
        self.job = HarmonyJobNotifier(client, config.job_id)
        if config.input_model_key:
            self.model_to_train = AdaptiveModel(path=f"model_registry://{config.input_model_key}")

    @classmethod
    def load(cls) -> Self:
        config = RecipeConfig()  # type: ignore
        return cls.from_config(config)

    @classmethod
    def from_config(cls, config: RecipeConfig) -> Self:
        client = get_client(
            config.harmony_url,
            num_gpus=config.num_gpus,
            api_key=config.api_key,
            use_case=config.use_case,
            compute_pool=config.compute_pool,
        )
        return cls(client, config)
