from asyncio import gather
from loguru import logger
from typing import Literal, Sequence, Any

from adaptive_harmony import StringThread
from adaptive_harmony.core.structured_output import JsonParseError
from adaptive_harmony.scoring.base_scorer import Scorer, ScoreWithMetadata
from adaptive_harmony.scoring.exceptions import IgnoreScoreException


class CombinedScorer(Scorer):
    """
    Combines scores from multiple scorers.
    Aggregates their results using weighted sum or average.
    Ignores failing scorers, proceeds calculating the aggregate score with the rest.
    """

    def __init__(
        self,
        scorers: Sequence[Scorer],
        weights: list[float] | None = None,
        aggregation_method: Literal["sum", "mean"] = "mean",
        failure_rate_warning_threshold: float = 0.2,
    ):
        super().__init__()
        self.scorers = scorers
        if weights:
            assert len(weights) == len(scorers), "Number of weights must match number of scorers"
        self.weights = weights or [1.0] * len(scorers)
        self.agg_method = aggregation_method
        self.failure_rate_warning_threshold = failure_rate_warning_threshold
        self.scorer_names = [s.__class__.__name__ for s in self.scorers]
        self.default_scorer_ids: list[int] = []
        name_counts = {}
        for name in self.scorer_names:
            count = name_counts.get(name, 0)
            self.default_scorer_ids.append(count)
            name_counts[name] = count + 1

    async def score(self, sample: StringThread) -> ScoreWithMetadata:

        async def separate_success_from_fail_scorers(scorer: Scorer) -> ScoreWithMetadata | None:
            try:
                return await scorer.score(sample)
            except (IgnoreScoreException, JsonParseError):
                # return None if score is supposed to be ignored, or judge output format failure
                return None
            except Exception as e:
                # fail for any other exception
                raise e

        tasks = [separate_success_from_fail_scorers(scorer) for scorer in self.scorers]
        results: list[ScoreWithMetadata | None] = await gather(*tasks)

        weighted_scores = []
        all_metadata = {}
        sub_scorers_metadata = []
        failed_scorers = []

        # Separate successful and failed results
        successful_results = []
        successful_weights = []

        for result, weight, scorer in zip(results, self.weights, self.scorers):
            if result is not None:
                # Successful scorer
                weighted_score = result.score * weight
                weighted_scores.append(weighted_score)
                successful_results.append(result)
                successful_weights.append(weight)

                sub_scorers_metadata.append(
                    dict(
                        scorer_type=scorer.__class__.__name__,
                        score=result.score,
                        weight=weight,
                        weighted_score=weighted_score,
                        metadata=result.metadata,
                        status="success",
                    )
                )
            else:
                # Failed scorer
                failed_scorers.append(scorer.__class__.__name__)
                sub_scorers_metadata.append(
                    dict(
                        scorer_type=scorer.__class__.__name__,
                        score=None,
                        weight=weight,
                        weighted_score=None,
                        metadata=None,
                        status="failed",
                    )
                )

        # Fail if no successfull scorers
        if not successful_results:
            raise RuntimeError("All scorers failed - cannot compute aggregate score")

        # Warn if more than a set % of scorers failed
        total_scorers = len(self.scorers)
        failure_rate = len(failed_scorers) / total_scorers
        if failure_rate > self.failure_rate_warning_threshold:
            logger.warning(f"{len(failed_scorers)}/{total_scorers}% of scorers failed for sample")

        all_metadata["sub_scorers"] = sub_scorers_metadata

        # Aggregate scores
        if self.agg_method == "sum":
            final_score = sum(weighted_scores)
        elif self.agg_method == "mean":
            # For average, we normalize by the sum of successful weights (renormalize)
            final_score = sum(weighted_scores) / sum(successful_weights)
        self.add_log({"score": final_score})

        # Add aggregation metadata
        all_metadata["aggregation"] = dict(
            agg_method=self.agg_method,
            total_weight=sum(self.weights),
            score=final_score,
            failure_rate=failure_rate,
        )

        score_with_metadata = ScoreWithMetadata(score=final_score, metadata=all_metadata)

        # Log the combined score and individual scorer results
        return score_with_metadata

    def get_logs(self, clear: bool = False) -> dict[str, Any]:
        # Get our own aggregated logs
        combined_logs = super().get_logs(clear=False)

        # Get logs from all individual scorers
        # If scorer has no logging name, attribute unique id within scorer type group as name
        all_logs = combined_logs
        for scorer, scorer_id, scorer_name in zip(
            self.scorers,
            self.default_scorer_ids,
            self.scorer_names,
        ):
            scorer_logs = scorer.get_logs(clear=clear)
            scorer_id_str = scorer.logging_name or str(scorer_id)
            all_logs = {
                **all_logs,
                **{f"{scorer_name}/{scorer_id_str}/{key}": value for key, value in scorer_logs.items()},
            }
        if clear:
            self.clear_logs()
        return all_logs

    def clear_logs(self) -> None:
        super().clear_logs()
        for scorer in self.scorers:
            scorer.clear_logs()
