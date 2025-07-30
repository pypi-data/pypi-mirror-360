# ruff: noqa: F403, F401
from .adaptive_harmony import (
    StringThread as StringThread,
    TokenizedThread as TokenizedThread,
    InferenceModel as InferenceModel,
    TrainingModel as TrainingModel,
    get_client as get_client,
    HarmonyClient as HarmonyClient,
    JobNotifier as JobNotifier,
    HarmonyJobNotifier as HarmonyJobNotifier,
)

from adaptive_harmony.core.dataset import DataSet
from adaptive_harmony.core.schedulers import CosineScheduler, CombinedSchedule, CosineSchedulerWithoutWarmup, Scheduler
from adaptive_harmony.metric_logger import WandbLogger, Logger
import adaptive_harmony.core.rl_utils as rl_utils


# Ensure key classes are available at module level
__all__ = [
    "StringThread",
    "TokenizedThread",
    "InferenceModel",
    "TrainingModel",
    "HarmonyClient",
    "get_client",
    "DataSet",
    "CosineScheduler",
    "CombinedSchedule",
    "CosineSchedulerWithoutWarmup",
    "Scheduler",
    "WandbLogger",
    "Logger",
    "rl_utils",
]


# Patch StringThread to use rich for display
from adaptive_harmony.core.display import _stringthread_repr, _tokenizedthread_repr

# Patch InferenceModel to have json output capabilities
from adaptive_harmony.core.structured_output import generate_and_validate, render_schema, render_pydantic_model

StringThread.__repr__ = _stringthread_repr
TokenizedThread.__repr__ = _tokenizedthread_repr
setattr(InferenceModel, "generate_and_validate", generate_and_validate)
setattr(InferenceModel, "render_schema", staticmethod(render_schema))
setattr(InferenceModel, "render_pydantic_model", staticmethod(render_pydantic_model))
