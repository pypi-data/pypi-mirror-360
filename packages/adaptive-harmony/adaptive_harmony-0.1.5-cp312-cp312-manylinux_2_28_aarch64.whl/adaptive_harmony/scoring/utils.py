from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict

from adaptive_harmony import StringThread

if TYPE_CHECKING:
    from adaptive_harmony import StringTurn


def validate_thread_last_assistant(thread: StringThread):
    turns = thread.get_turns()
    assert len(turns) > 0, "The thread must have at least one turn"
    assert turns[-1].role == "assistant", "The last turn must be an assistant turn"


def separate_context_from_last_user_turn(
    thread: StringThread,
    include_system_prompt: bool = False,
) -> tuple[list[StringTurn], str | None]:
    """
    Separates turns into context and last user turn.
    Includes system prompt in context if include_system_prompt is True.
    If there is no user turn, last user turn is None.
    """
    validate_thread_last_assistant(thread)
    turns = thread.get_turns()

    # Possibly remove system prompt
    if not include_system_prompt and turns[0].role == "system":
        turns = turns[1:]

    # Find last user turn
    user_question = None
    user_question_idx = -1
    for i, turn in enumerate(turns):
        if turn.role == "user":
            user_question = turn.content
            user_question_idx = i

    if user_question is None:
        # Last turn is guaranteed to be assistant due to validate_thread_last_assistant
        context_turns = turns[:-1]
    else:
        context_turns = turns[:user_question_idx]

    return context_turns, user_question


class SuccessJudgeLog(TypedDict):
    prompt: str
    reasoning: str
    score: float


class FailedJudgeLog(TypedDict):
    prompt: str
    error: str | None
