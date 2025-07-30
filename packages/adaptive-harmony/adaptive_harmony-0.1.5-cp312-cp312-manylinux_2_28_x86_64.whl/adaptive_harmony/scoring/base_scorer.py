from abc import ABC, abstractmethod
from adaptive_harmony import StringThread
from adaptive_harmony.logging_table import Table
from typing import Any, Callable, Awaitable
from dataclasses import dataclass, field
from collections import defaultdict
import statistics


@dataclass
class ScoreWithMetadata:
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class Scorer(ABC):
    """
    BaseScorer to inherit from when building a scoring function.
    """

    def __init__(self, logging_name: str | None = None):
        self._logs: list[dict[str, Any]] = []
        self.logging_name = logging_name

    @abstractmethod
    async def score(self, sample: StringThread) -> ScoreWithMetadata:
        """
        Score a single sample.
        Returns a single float score, with optional metadata.
        Metadata can be useful for evals when LLM reasoning regarding the score is available.
        """
        pass

    async def score_without_metadata(self, sample: StringThread) -> float:
        """Returns only the float score from .score"""
        return (await self.score(sample)).score

    def add_log(self, log_data: dict[str, Any]) -> None:
        """Add a log entry to the scorer's log collection."""
        self._logs.append(log_data)

    def get_logs(self, clear: bool = False) -> dict[str, float | Table]:
        """
        Get aggregated logs from all score calls.
        Base implementation computes statistics for "score" keys in individual logs.
        If there are none, returns empty dict.
        """
        if not self._logs:
            return {}

        scores = [s for s in [log.get("score") for log in self._logs] if s is not None]
        logs = {}
        if scores:
            logs.update(dict(
                **{
                    f"score/{key}": value
                    for key, value in dict(
                        mean=statistics.mean(scores),
                        std=statistics.stdev(scores) if len(scores) > 1 else 0.0,
                        min=min(scores),
                        max=max(scores),
                        count=len(scores),
                    ).items()
                },
            ))
        if clear:
            self.clear_logs()
        return logs

    def clear_logs(self) -> None:
        """
        Clear all accumulated logs.
        """
        self._logs.clear()

    @classmethod
    def from_function(cls, async_fn: Callable[[StringThread], Awaitable[float]]) -> "Scorer":
        class FunctionScorer(cls):
            def __init__(self):
                super().__init__()

            async def score(self, sample: StringThread) -> ScoreWithMetadata:
                result = await async_fn(sample)
                score_with_metadata = ScoreWithMetadata(score=result, metadata={})
                self.add_log({"score": result})
                return score_with_metadata

        return FunctionScorer()
