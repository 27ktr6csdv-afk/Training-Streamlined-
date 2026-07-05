"""Roulette payout drill (double-zero wheel).

Standard American payout schedule:

* Straight up ............. 35:1
* Split ................... 17:1
* Street (3 numbers) ...... 11:1
* Corner (4 numbers) ...... 8:1
* Top line 0-00-1-2-3 ..... 6:1
* Six line (2 streets) .... 5:1
* Dozen / Column .......... 2:1
* Red/Black, Odd/Even,
  High/Low ................ 1:1
"""

from __future__ import annotations

import random
from decimal import Decimal

from .quiz import Question, fmt_money

INSIDE_BETS = {
    "STRAIGHT UP on 17": 35,
    "STRAIGHT UP on 00": 35,
    "SPLIT on 8/11": 17,
    "SPLIT on 0/00": 17,
    "STREET on 13-14-15": 11,
    "CORNER on 25-26-28-29": 8,
    "TOP LINE (0-00-1-2-3)": 6,
    "SIX LINE on 19-24": 5,
}
OUTSIDE_BETS = {
    "FIRST DOZEN (1-12)": 2,
    "THIRD COLUMN": 2,
    "RED": 1,
    "BLACK": 1,
    "ODD": 1,
    "HIGH (19-36)": 1,
}
CHIP_AMOUNTS = [Decimal(b) for b in (1, 2, 3, 5, 8, 10, 15, 20, 25, 50)]


def single_bet_question(rng: random.Random) -> Question:
    inside = rng.random() < 0.7
    table = INSIDE_BETS if inside else OUTSIDE_BETS
    name = rng.choice(list(table))
    odds = table[name]
    bet = rng.choice(CHIP_AMOUNTS)
    win = bet * odds
    return Question(
        prompt=(
            f"The ball lands and a player's {fmt_money(bet)} {name} bet wins. "
            "How much do you pay?"
        ),
        answer=win,
        explanation=f"{name.title()} pays {odds}:1 — {fmt_money(bet)} pays {fmt_money(win)}.",
    )


def stacked_bet_question(rng: random.Random) -> Question:
    """A winning number covered by several bets — pay the whole picture."""
    number = 17
    coverage = [
        (f"STRAIGHT UP on {number}", 35),
        (f"SPLIT on {number}/20", 17),
        (f"CORNER on 16-17-19-20", 8),
        (f"STREET on 16-17-18", 11),
        (f"SECOND DOZEN (13-24)", 2),
    ]
    picks = rng.sample(coverage, rng.choice([2, 3]))
    lines = []
    total = Decimal(0)
    breakdown = []
    for name, odds in picks:
        bet = rng.choice(CHIP_AMOUNTS[:6])
        lines.append(f"  {fmt_money(bet)} {name}")
        pay = bet * odds
        total += pay
        breakdown.append(f"{fmt_money(bet)} at {odds}:1 = {fmt_money(pay)}")
    bets_text = "\n".join(lines)
    return Question(
        prompt=(
            f"The ball lands on {number}. One player has all of these "
            f"winning bets:\n{bets_text}\n"
            "What is the TOTAL payout to this player?"
        ),
        answer=total,
        explanation=" + ".join(breakdown) + f" = {fmt_money(total)}.",
    )


def make_question(rng: random.Random | None = None) -> Question:
    rng = rng or random.Random()
    if rng.random() < 0.3:
        return stacked_bet_question(rng)
    return single_bet_question(rng)
