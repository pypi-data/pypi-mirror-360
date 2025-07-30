import pysbd
from typing import Literal
from pydantic import BaseModel, Field


from adaptive_harmony import InferenceModel, StringThread
from adaptive_harmony.core.utils import stringify_thread
from adaptive_harmony.scoring import Scorer, ScoreWithMetadata
from adaptive_harmony.scoring.exceptions import IgnoreScoreException
from adaptive_harmony.scoring.faithfulness_judge_scorer.prompts import SYSTEM, USER
from adaptive_harmony.scoring.utils import validate_thread_last_assistant, separate_context_from_last_user_turn


class SingleStatementFaithfulnessJudgeOutput(BaseModel):
    statement_idx: int = Field(description="The original index of the sentence being scored")
    reasoning: str = Field(description="Reasoning to support the rationale behind the score")
    score: Literal["1", "0"] = Field(
        description="The score of the sample, 1 if the statement is fully supported by the context, 0 if it is not"
    )


class FaithfulnessScorerOutput(BaseModel):
    all_statements_scoring: list[SingleStatementFaithfulnessJudgeOutput] = Field(
        description="An array of objects, each analyzing a single statement from the original list of statements"
    )


SupportedLanguages = Literal[
    "en",
    "hi",
    "mr",
    "zh",
    "es",
    "am",
    "ar",
    "hy",
    "bg",
    "ur",
    "ru",
    "pl",
    "fa",
    "nl",
    "da",
    "fr",
    "my",
    "el",
    "it",
    "ja",
    "de",
    "kk",
    "sk",
]


class FaithfulnessScorer(Scorer):
    """
    Scores each sentence in the last assistant turn as fully supported by the context or not (1 or 0).
    The context is the rest of the thread, excluding the system prompt.
    The final score is the average of each sentence.
    Requires an input language code to split the sentences.
    """

    def __init__(
        self,
        model: InferenceModel,
        language: SupportedLanguages,
        logging_name: str | None = None,
    ):
        super().__init__(logging_name)
        self.model = model
        self.language = language
        self.sentence_splitter = pysbd.Segmenter(language=language)

    async def score(self, thread: StringThread) -> ScoreWithMetadata:
        # Split response into sentences
        validate_thread_last_assistant(thread)
        # Separate conversation context from last user turn
        context_turns, user_question = separate_context_from_last_user_turn(thread)
        completion = thread.last_content()
        split_sentences = self.sentence_splitter.segment(completion)
        sentences = [f"{i}: {sentence.strip()}" for i, sentence in enumerate(split_sentences) if sentence.strip()]
        sentences_judge_str = "\n".join(sentences)

        # Build prompt
        context_str = stringify_thread(StringThread(context_turns))
        judge_thread = (
            StringThread()
            .system(SYSTEM.format(json_schema=self.model.render_schema(FaithfulnessScorerOutput)))
            .user(USER.format(context=context_str, user_question=user_question, sentences=sentences_judge_str))
        )

        # Generate response
        try:
            _, parsed_response = await self.model.temperature(0.0).generate_and_validate(
                judge_thread, FaithfulnessScorerOutput
            )
        except Exception as e:
            raise IgnoreScoreException(f"Failed to judge sentences: {e}")
        
        # Raise error if judge failed to judge any sentence
        n_judged_sentences = len(parsed_response.all_statements_scoring)
        if n_judged_sentences != len(sentences):
            raise IgnoreScoreException(
                f"Number of sentences in the response ({n_judged_sentences})"
                f"does not match the number of sentences in the input ({len(sentences)})"
            )
        # Calculate avg score
        score = round(
            sum([float(judgement.score) for judgement in parsed_response.all_statements_scoring]) / n_judged_sentences,
            3,
        )
        # Add per sentence reasoning and score metadata
        metadata = [
            dict(
                sentence_idx=judgement.statement_idx,
                reasoning=judgement.reasoning,
                score=judgement.score,
            )
            for judgement in parsed_response.all_statements_scoring
        ]
        self.add_log({"score": score})
        return ScoreWithMetadata(score=score, metadata=dict(per_sentence=metadata))
