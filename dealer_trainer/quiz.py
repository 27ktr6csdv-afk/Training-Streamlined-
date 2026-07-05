"""Shared quiz engine used by every game drill.

A drill is just a callable that returns a :class:`Question`.  The engine
handles prompting, answer parsing (money or text), scoring, and showing the
explanation whenever the trainee misses one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Callable, Optional, Sequence, Union

Answer = Union[Decimal, str]


@dataclass
class Question:
    """A single quiz question.

    ``answer`` may be a Decimal (a dollar amount, compared numerically) or a
    string (compared case-insensitively).  ``accept`` lists extra strings that
    also count as correct, e.g. "s17" for "soft 17".
    """

    prompt: str
    answer: Answer
    explanation: str = ""
    accept: Sequence[str] = field(default_factory=tuple)


def parse_money(text: str) -> Optional[Decimal]:
    """Parse '$37.50', '37.5', '1,250', '40' -> Decimal, or None if invalid."""
    cleaned = text.strip().lstrip("$").replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def fmt_money(amount: Decimal) -> str:
    """Format a Decimal as $40 or $37.50 (no trailing .00)."""
    amount = amount.quantize(Decimal("0.01"))
    if amount == amount.to_integral_value():
        return f"${amount:,.0f}"
    return f"${amount:,.2f}"


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def is_correct(question: Question, response: str) -> bool:
    if isinstance(question.answer, Decimal):
        value = parse_money(response)
        return value is not None and value == question.answer
    normalized = _normalize(response)
    if normalized == _normalize(question.answer):
        return True
    return any(normalized == _normalize(alt) for alt in question.accept)


def format_answer(question: Question) -> str:
    if isinstance(question.answer, Decimal):
        return fmt_money(question.answer)
    return question.answer


def run_drill(
    title: str,
    make_question: Callable[[], Question],
    num_questions: int = 10,
    input_fn: Callable[[str], str] = input,
    print_fn: Callable[[str], None] = print,
) -> tuple[int, int]:
    """Run an interactive drill.  Returns (correct, attempted).

    The trainee can type 'q' to end the drill early.
    """
    print_fn("")
    print_fn("=" * 62)
    print_fn(f"  {title}")
    print_fn("=" * 62)
    print_fn("Answer each question. Dollar answers may include a '$'.")
    print_fn("Type 'q' at any prompt to end the drill early.")

    correct = attempted = 0
    for number in range(1, num_questions + 1):
        question = make_question()
        print_fn("")
        print_fn(f"--- Question {number} of {num_questions} ---")
        print_fn(question.prompt)
        try:
            response = input_fn("> ")
        except EOFError:
            break
        if response.strip().lower() in ("q", "quit", "exit"):
            break
        attempted += 1
        if is_correct(question, response):
            correct += 1
            print_fn("  Correct!")
        else:
            print_fn(f"  Not quite. Correct answer: {format_answer(question)}")
        if question.explanation:
            print_fn(f"  {question.explanation}")

    print_fn("")
    if attempted:
        pct = 100 * correct / attempted
        print_fn(f"Drill complete: {correct}/{attempted} correct ({pct:.0f}%).")
        if pct == 100:
            print_fn("Perfect score — table ready!")
        elif pct >= 80:
            print_fn("Solid. Keep drilling the ones you missed.")
        else:
            print_fn("Keep practicing — review the explanations above.")
    else:
        print_fn("No questions answered.")
    return correct, attempted
