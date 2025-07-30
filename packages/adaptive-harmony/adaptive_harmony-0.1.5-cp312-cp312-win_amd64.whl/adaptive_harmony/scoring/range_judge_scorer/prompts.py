import textwrap
from typing import NamedTuple
from adaptive_harmony import StringThread

TEMPLATE = "{task_introduction}\n\nEvaluation Criteria:\n{evaluation_criteria}\nEvaluation Steps:\n{evaluation_steps}\nExample:\n\n  Source Transcript:\n{transcript}\n\nSummary:\n{summary}\n\nEvaluation Form (scores ONLY):\n\n- {metric}: "


class SubrangeExpectations(NamedTuple):
    subrange: tuple[int, int]
    expectation: str


COMMON_EVALUATION_PROMPT = """You are an expert evaluator of AI-user interactions.
You will be given:
- CONTEXT : previous conversation history, might be empty
- LAST USER INPUT : the latest input from the user
- ASSISTANT ANSWER : the latest answer from the AI
- EVALUATION STEPS : logical reasoning steps to take when evaluating the interaction
"""


class RangeScorerTemplates:
    @staticmethod
    def get_evaluation_steps(criteria: str) -> StringThread:
        return (
            StringThread()
            .system(
                textwrap.dedent(
                    """\
                    Given an evaluation criteria which outlines how you should judge an interaction between an AI and a user, generate 3-4 concise evaluation steps based on the criteria below.

                    Return your evaluation steps as a numbered list of evaluation steps, such as:

                    Steps list:
                    1. First step
                    2. Second step
                    3. Third step
                    etc.

                    Focus on specific, concise steps that can be objectively followed based on the evaluation criteria provided.
                    Don't return any preamble or explanation, only the list.
                    """
                )
            )
            .user(f"Evaluation Criteria:\n{criteria}\nSteps list:\n")
        )

    @staticmethod
    def get_json_reasoned_score(
        context: str,
        last_user_input: str,
        assistant_answer: str,
        evaluation_steps: str,
        score_range: tuple[int, int],
        json_schema: str,
        subrange_expectations: list[SubrangeExpectations] | None = None,
    ) -> StringThread:
        if subrange_expectations:
            subrange_expectations_str = "which should correspond to:\n" + "\n".join(
                [
                    f"{sub.subrange[0]} - {sub.subrange[1]}: {sub.expectation}"
                    for i, sub in enumerate(subrange_expectations)
                ]
            )
        else:
            subrange_expectations_str = f"where {score_range[1]} indicates strong alignment with the evaluation steps and {score_range[0]} indicates no alignment."

        system_prompt = (
            COMMON_EVALUATION_PROMPT
            + f"""
Your task is to evaluate and score the ASSISTANT ANSWER, strictly following the EVALUATION STEPS.
You must respond with a valid JSON object that matches the following schema:

{json_schema}

Your reasoning for the score:
- Be specific and grounded in the evaluation steps
- Mention specific details, strenghts or shortcomings of the answer, referencing relevant details from the input
- Be concise, clear, and focused on the evaluation logic.
- **Never** quote the score itself in the explanation; focus only on reasoning through the evaluation steps

Your final evaluation score must be strictly within the range of [{score_range[0]} - {score_range[1]}], {subrange_expectations_str}

Return only the JSON object after the OUTPUT header, no other text, preamble or explanation.
"""
        )

        user_prompt = (
            f"CONTEXT\n{context}\n\n"
            f"LAST USER INPUT\n{last_user_input}\n\n"
            f"ASSISTANT ANSWER\n{assistant_answer}\n\n"
            f"EVALUATION STEPS\n{evaluation_steps}\n\n"
            "JSON OUTPUT\n"
        )

        return StringThread().system(system_prompt).user(user_prompt)

    @staticmethod
    def get_up_to_score(
        context: str,
        last_user_input: str,
        assistant_answer: str,
        evaluation_steps: str,
        score_range: tuple[int, int],
        reasoning: str,
        subrange_expectations: list[SubrangeExpectations] | None = None,
    ) -> StringThread:
        if subrange_expectations:
            subrange_expectations_str = "which should correspond to:\n" + "\n".join(
                [
                    f"{sub.subrange[0]} - {sub.subrange[1]}: {sub.expectation}"
                    for i, sub in enumerate(subrange_expectations)
                ]
            )
        else:
            subrange_expectations_str = f"where {score_range[1]} indicates strong alignment with the evaluation steps and {score_range[0]} indicates no alignment."

        system_prompt = COMMON_EVALUATION_PROMPT + textwrap.dedent(
            f"""\
                - REASONING : the reasoning for the score, following the logic of the evaluations steps for the interaction being evaluated

                You must respond only with a score, based on the original EVALUATION_STEPS and the REASONING for the sample,
                which should justify your score for the sample.

                Your final evaluation score must be strictly within the range of [{score_range[0]} - {score_range[1]}], {subrange_expectations_str}

                Return only the integer score, nothing before or after.
                """
        )
        user_prompt = (
            f"CONTEXT\n{context}\n\n"
            f"LAST USER INPUT\n{last_user_input}\n\n"
            f"ASSISTANT ANSWER\n{assistant_answer}\n\n"
            f"EVALUATION STEPS\n{evaluation_steps}\n\n"
            f"REASONING\n{reasoning}\n\n"
            "SCORE: "
        )

        return StringThread().system(system_prompt).user(user_prompt)
