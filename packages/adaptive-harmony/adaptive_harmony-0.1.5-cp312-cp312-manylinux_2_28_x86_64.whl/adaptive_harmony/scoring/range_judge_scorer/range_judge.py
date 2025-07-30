import asyncio
import numpy as np
from pydantic import BaseModel, Field
from random import shuffle


from adaptive_harmony import InferenceModel, StringThread
from adaptive_harmony.core.utils import stringify_thread
from adaptive_harmony.logging_table import Table
from adaptive_harmony.scoring import Scorer, ScoreWithMetadata
from adaptive_harmony.scoring.range_judge_scorer.prompts import RangeScorerTemplates, SubrangeExpectations
from adaptive_harmony.scoring.utils import (
    validate_thread_last_assistant,
    separate_context_from_last_user_turn,
    SuccessJudgeLog,
    FailedJudgeLog,
)


class ReasonedScore(BaseModel):
    reasoning: str = Field(description="String reasoning to support the rationale behind the score")
    score: int = Field(description="Integer score for the interaction, must be within the specified score range")


class RangeJudgeScorer(Scorer):
    """
    Scores a thread in a range of integer scores, based on a list of evaluation steps.
    If evaluation steps are not provided, they are generated from the criteria.
    The final score is computed as a weighted average of all possible scores,
    where the weights are the logprobs of each score.
    You can pass subrange_expectations to the scorer, to help the judge
    understand the correspondence between score subranges and expected quality levels.
    """

    def __init__(
        self,
        model: InferenceModel,
        criteria: str,
        score_range: tuple[int, int] = (1, 5),
        evaluation_steps: list[str] | None = None,
        subrange_expectations: list[SubrangeExpectations] | None = None,
        normalize_score: bool = True,
        logging_name: str | None = None,
    ):
        model_path: str = model.get_builder_args()["path"]
        assert model_path.startswith("model_registry://"), "External models cannot be used in RangeJudgeScorer"

        super().__init__(logging_name)
        self._logs: list[SuccessJudgeLog | FailedJudgeLog] = []  # already created in super, this is for typing
        self.model = model
        self.criteria = criteria
        self.score_range = score_range
        self.min_score, self.max_score = score_range
        self.subrange_expectations = subrange_expectations
        self.normalize_score = normalize_score

        if evaluation_steps is None:
            self._str_evaluation_steps = None
            self._list_eval_steps = None
        else:
            self._str_evaluation_steps = "\n".join([f"{i + 1}: {step}" for i, step in enumerate(evaluation_steps)])
            self._list_eval_steps = evaluation_steps

    @property
    def evaluation_steps(self) -> list[str] | None:
        return self._list_eval_steps

    @property
    def str_evaluation_steps(self) -> str | None:
        return self._str_evaluation_steps

    @evaluation_steps.setter
    def evaluation_steps(self, steps: list[str]):
        self._list_eval_steps = steps
        self._str_evaluation_steps = "\n".join([f"{i + 1}: {step}" for i, step in enumerate(steps)])

    async def generate_evaluation_steps(self) -> list[str]:
        thread = await self.model.temperature(0.0).generate(RangeScorerTemplates.get_evaluation_steps(self.criteria))
        self._str_evaluation_steps = thread.last_content()
        self._list_eval_steps = self._str_evaluation_steps.split("\n")
        assert self.evaluation_steps
        return self.evaluation_steps

    async def score(self, thread: StringThread) -> ScoreWithMetadata:
        if self.evaluation_steps is None:
            await self.generate_evaluation_steps()

        validate_thread_last_assistant(thread)
        context_turns, last_user_turn = separate_context_from_last_user_turn(thread)
        context_str = stringify_thread(StringThread(context_turns))
        last_assistant_turn = thread.last_content()

        assert last_user_turn is not None, "There must be at least one user turn"

        assert self.str_evaluation_steps
        eval_thread = RangeScorerTemplates.get_json_reasoned_score(
            context=context_str,
            last_user_input=last_user_turn,
            assistant_answer=last_assistant_turn,
            evaluation_steps=self.str_evaluation_steps,
            score_range=self.score_range,
            json_schema=self.model.render_schema(ReasonedScore),
            subrange_expectations=self.subrange_expectations,
        )
        reasoned_score = (await self.model.temperature(0.0).generate_and_validate(eval_thread, ReasonedScore))[1]

        # Get a prompt that includes the reasoning for the sample, all the way to form filling the score
        up_to_score_thread = RangeScorerTemplates.get_up_to_score(
            context=context_str,
            last_user_input=last_user_turn,
            assistant_answer=last_assistant_turn,
            evaluation_steps=self.str_evaluation_steps,
            score_range=self.score_range,
            reasoning=reasoned_score.reasoning,
            subrange_expectations=self.subrange_expectations,
        )

        # Get logprobs for each possible final
        possible_score_ints = [s for s in range(self.min_score, self.max_score + 1)]
        logprobs = await asyncio.gather(
            *[self.model.temperature(0.0).logprobs(up_to_score_thread.assistant(f"{s}")) for s in possible_score_ints]
        )

        # Convert to probabilities and compute weighted average
        probs = np.exp(logprobs - np.logaddexp.reduce(logprobs))
        weighted_score = np.average(possible_score_ints, weights=probs)

        final_score: float = weighted_score
        if self.normalize_score:  # normalize to 0-1 range
            final_score = (weighted_score - self.min_score) / (self.max_score - self.min_score)

        str_prompt = stringify_thread(eval_thread, sep=f"\n\n{'-'*10}\n\n")
        self.add_log({"score": final_score, "prompt": str_prompt, "reasoning": reasoned_score.reasoning})

        metadata = dict(
            criteria=self.criteria,
            raw_avg_score=float(weighted_score),
            scale_range=(self.min_score, self.max_score),
            score_probabilities={str(score): float(prob) for score, prob in zip(possible_score_ints, probs)},
            evaluation_steps=self.evaluation_steps,
            reasoning=reasoned_score.reasoning,
        )

        return ScoreWithMetadata(score=float(final_score), metadata=metadata)

    def add_log(self, log: SuccessJudgeLog | FailedJudgeLog) -> None:
        self._logs.append(log)

    def get_logs(self, clear: bool = False) -> dict[str, float | Table]:
        # Only clear logs at the end if clear is True
        logs = super().get_logs(clear=False)

        # create Successfully Scored Samples Table
        successfully_scored_samples = [log for log in self._logs if "score" in log]
        # sort samples by score for percentile-based sampling
        sorted_samples = sorted(successfully_scored_samples, key=lambda x: x["score"])
        total_samples = len(sorted_samples)

        if total_samples >= 15:
            # sample 15 samples distributed across percentiles
            indices = []
            for i in range(15):
                # calculate percentile position (0% to 100% spread across 15 samples)
                percentile = i / 14  # 14 intervals for 15 samples
                index = int(percentile * (total_samples - 1))
                indices.append(index)

            subset_successfully_scored_samples = [sorted_samples[i] for i in indices]
        else:
            # if we have fewer than 15 samples, take them all
            subset_successfully_scored_samples = sorted_samples
        scored_samples = (
            Table()
            .add_column("Prompt", [log["prompt"] for log in subset_successfully_scored_samples])
            .add_column("Reasoning", [str(log["reasoning"]) for log in subset_successfully_scored_samples])
            .add_column("Score", [float(log["score"]) for log in subset_successfully_scored_samples])
        )
        logs["score/scored_samples"] = scored_samples
        if clear:
            self.clear_logs()

        return logs
