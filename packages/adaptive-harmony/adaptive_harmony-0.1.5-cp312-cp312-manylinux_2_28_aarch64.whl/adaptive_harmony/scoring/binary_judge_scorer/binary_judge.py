from pydantic import BaseModel, Field
from typing import Literal, TypedDict
from random import shuffle
import json
import json

from adaptive_harmony import StringThread, InferenceModel
from adaptive_harmony.core.utils import SingleTurnShot, stringify_thread
from adaptive_harmony.logging_table import Table
from adaptive_harmony.scoring import Scorer, ScoreWithMetadata
from adaptive_harmony.scoring.binary_judge_scorer.prompts import BinaryJudgeShot, SYSTEM, USER, DEFAULT_SHOTS
from adaptive_harmony.scoring.exceptions import IgnoreScoreException
from adaptive_harmony.scoring.utils import (
    validate_thread_last_assistant,
    separate_context_from_last_user_turn,
    SuccessJudgeLog,
    FailedJudgeLog,
)


class BinaryJudgeOutput(BaseModel):
    reasoning: str = Field(description="Reasoning to support the rationale behind the score")
    score: Literal["PASS", "FAIL", "NA"] = Field(description="The score for the sample")


class ScoresMap(TypedDict):
    PASS: float
    FAIL: float


class BinaryJudgeScorer(Scorer):
    """
    Binary judge for scoring samples as PASS, FAIL or NA using few-shot prompting.
    If custom shots are provided, they are used instead of the default shots.
    """

    def __init__(
        self,
        model: InferenceModel,
        criteria: str,
        shots: list[BinaryJudgeShot] | None = None,
        logging_name: str | None = None,
    ):
        super().__init__(logging_name)
        self._logs: list[SuccessJudgeLog | FailedJudgeLog] = []  # already created in super, this is for typing
        self.model = model
        self.criteria = criteria
        # Score mapping
        self.scores_map: ScoresMap = {"PASS": 1.0, "FAIL": 0.0}

        self._original_shots = shots or DEFAULT_SHOTS
        self._shots = self.format_user_shots(shots or DEFAULT_SHOTS)

    @property
    def shots(self) -> list[BinaryJudgeShot]:
        return self._original_shots

    @shots.setter
    def shots(self, shots: list[BinaryJudgeShot]):
        self._original_shots = shots
        self._shots = self.format_user_shots(shots)

    @staticmethod
    def extract_user_template_kwargs(thread: StringThread) -> dict[str, str]:

        validate_thread_last_assistant(thread)
        # Separate conversation context from last user turn
        context_turns, user_question = separate_context_from_last_user_turn(thread)
        context_str = stringify_thread(StringThread(context_turns))
        completion = thread.last_content()

        assert user_question, "There must be at least one user turn"
        return dict(
            context=context_str,
            user_question=user_question,
            completion=completion,
        )

    def format_user_shots(self, shots: list[BinaryJudgeShot]) -> list[SingleTurnShot]:
        """
        Turn a possibly multi turn example into a single turn one,
        with appropriate kwargs to format the task's prompt templates
        """
        new_shots: list[SingleTurnShot] = []
        for shot in shots:
            user_template_kwargs = self.extract_user_template_kwargs(shot.thread)
            user_template_kwargs["criteria"] = shot.criteria or self.criteria
            single_turn_shot = SingleTurnShot(
                user=user_template_kwargs,
                assistant={
                    "json_answer": self.model.render_pydantic_model(
                        BinaryJudgeOutput(
                            reasoning=shot.reasoning,
                            score=shot.score,
                        )
                    )
                },
            )
            new_shots.append(single_turn_shot)

        return new_shots

    def get_judge_prompt(self, thread: StringThread) -> StringThread:
        """Build the judging prompt for a given sample."""
        # build the real user template kwargs
        user_template_kwargs = self.extract_user_template_kwargs(thread)
        user_template_kwargs["criteria"] = self.criteria
        # system kwarg
        output_json_schema = self.model.render_schema(BinaryJudgeOutput)

        # system
        prompt = StringThread().system(SYSTEM.format(json_schema=output_json_schema))
        # shots
        for shot in self._shots:
            prompt = prompt.user(USER.format(**shot["user"]))
            prompt = prompt.assistant(shot["assistant"]["json_answer"])
        # real input
        prompt = prompt.user(USER.format(**user_template_kwargs))

        return prompt

    async def score(self, sample: StringThread) -> ScoreWithMetadata:
        judging_prompt = self.get_judge_prompt(sample)
        try:
            _, parsed_output = await self.model.temperature(0.0).generate_and_validate(
                judging_prompt, BinaryJudgeOutput
            )

            float_score = self.scores_map.get(parsed_output.score)
            str_prompt = stringify_thread(judging_prompt, sep=f"\n\n{'-'*10}\n\n")
            # NA case, ignore score
            if float_score is None:
                self.add_log({"prompt": str_prompt, "error": f"Non applicable score: {parsed_output.reasoning}"})
                raise IgnoreScoreException(f"Non applicable score: {parsed_output.reasoning}")

            else:
                score_with_metadata = ScoreWithMetadata(
                    score=float_score, metadata={"reasoning": parsed_output.reasoning}
                )
                self.add_log({"score": float_score, "prompt": str_prompt, "reasoning": parsed_output.reasoning})

                return score_with_metadata
        except Exception as e:
            raise e

    def add_log(self, log: SuccessJudgeLog | FailedJudgeLog) -> None:
        self._logs.append(log)

    def get_logs(self, clear: bool = False) -> dict[str, float | Table]:
        # Only clear logs at the end if clear is True
        logs = super().get_logs(clear=False)

        # create Successfully Scored Samples Table (up to 5 samples each for score 0 and 1)
        successfully_scored_samples = [log for log in self._logs if "score" in log]
        shuffle(successfully_scored_samples)
        samples_score_0 = [log for log in successfully_scored_samples if log["score"] == self.scores_map["FAIL"]][:5]
        samples_score_1 = [log for log in successfully_scored_samples if log["score"] == self.scores_map["PASS"]][:5]
        subset_successfully_scored_samples = samples_score_0 + samples_score_1
        scored_samples = (
            Table()
            .add_column("Prompt", [log["prompt"] for log in subset_successfully_scored_samples])
            .add_column("Reasoning", [str(log["reasoning"]) for log in subset_successfully_scored_samples])
            .add_column("Score", [float(log["score"]) for log in subset_successfully_scored_samples])
        )
        logs["score/scored_samples"] = scored_samples

        # create Failed Scored Samples Table
        failed_scored_samples = [log for log in self._logs if "error" in log]
        unscored_samples = (
            Table()
            .add_column("Prompt", [log["prompt"] for log in failed_scored_samples])
            .add_column("Error", [str(log["error"]) for log in failed_scored_samples])
        )
        logs["score/unscored_samples"] = unscored_samples
        logs["score/unscored_samples_count"] = len(failed_scored_samples)

        if clear:
            self.clear_logs()

        return logs

    @classmethod
    def from_playground_export(
        cls, model: InferenceModel, shots: list[dict], logging_name: str | None = None
    ) -> "BinaryJudgeScorer":
        """
        Create a BinaryJudgeScorer from a list of shots exported from the Playground.

        Example of shots:
        [
            {
                "criteria": "The assistant should give a number between 1 and 10",
                "judgement": "{\n  \"reasoning\": \"The given completion is a number, but it is not between 1 and 10.\",\n  \"score\": \"FAIL\"\n}",
                "thread": [
                    [
                        "user",
                        "Give me a number"
                    ],
                    [
                        "assistant",
                        "12"
                    ]
                ]
            },
            ...
        ]
        """
        if not shots:
            raise ValueError("No shots provided")

        criteria = shots[0]["criteria"]
        for shot in shots:
            if shot["criteria"] != criteria:
                raise ValueError("All shots do not have the same criteria")

        formatted_shots = []
        for shot in shots:
            judgement = json.loads(shot["judgement"])
            formatted_shots.append(
                BinaryJudgeShot(
                    criteria=shot["criteria"],
                    reasoning=judgement["reasoning"],
                    score=judgement["score"],
                    thread=StringThread([tuple(turn) for turn in shot["thread"]]),
                )
            )

        return cls(
            model=model,
            criteria=criteria,
            shots=formatted_shots,
            logging_name=logging_name,
        )
