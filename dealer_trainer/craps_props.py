"""Craps proposition (center-table) drill.

Payout schedule used (a common Las Vegas card, paid "to one"):

* Hard 4 / Hard 10 ........ 7:1
* Hard 6 / Hard 8 ......... 9:1
* Any Seven ............... 4:1
* Any Craps ............... 7:1
* Aces (2) / Twelve (12) .. 30:1
* Ace-Deuce (3) / Yo (11) . 15:1
* Horn, C&E and World are split bets — the drill quizzes the NET payout
  (winning part paid, losing parts collected), which is how the stick calls it.
"""

from __future__ import annotations

import random
from decimal import Decimal

from .quiz import Question, fmt_money

HARDWAYS = {4: 7, 10: 7, 6: 9, 8: 9}
ONE_ROLL = {
    "Any Seven": (4, "the shooter rolls a 7"),
    "Any Craps": (7, "the shooter rolls craps (a 3)"),
    "Aces": (30, "the shooter rolls a 2"),
    "Twelve": (30, "the shooter rolls a 12"),
    "Ace-Deuce": (15, "the shooter rolls a 3"),
    "Yo (eleven)": (15, "the shooter rolls a yo — 11"),
}
PROP_BETS = [Decimal(b) for b in (1, 2, 5, 10, 25)]


def hardway_question(rng: random.Random) -> Question:
    number = rng.choice(list(HARDWAYS))
    odds = HARDWAYS[number]
    bet = rng.choice(PROP_BETS)
    win = bet * odds
    half = number // 2
    return Question(
        prompt=(
            f"A player has {fmt_money(bet)} on the HARD {number} and the "
            f"shooter rolls {half}-{half}. How much do you pay?"
        ),
        answer=win,
        explanation=(
            f"Hard {number} pays {odds}:1 — {fmt_money(bet)} pays "
            f"{fmt_money(win)}. (Hard 4 and 10 pay 7:1; hard 6 and 8 pay 9:1.)"
        ),
    )


def one_roll_question(rng: random.Random) -> Question:
    name = rng.choice(list(ONE_ROLL))
    odds, roll = ONE_ROLL[name]
    bet = rng.choice(PROP_BETS)
    win = bet * odds
    return Question(
        prompt=(
            f"A player has {fmt_money(bet)} on {name.upper()} and {roll}. "
            "How much do you pay?"
        ),
        answer=win,
        explanation=f"{name} pays {odds}:1 — {fmt_money(bet)} pays {fmt_money(win)}.",
    )


def horn_question(rng: random.Random) -> Question:
    units = rng.choice([1, 2, 5])
    bet = Decimal(4 * units)  # $1 unit on each of 2, 3, 11, 12
    roll = rng.choice([2, 3, 11, 12])
    odds = 30 if roll in (2, 12) else 15
    win = Decimal(units) * odds - Decimal(3 * units)  # losing 3 parts come down
    return Question(
        prompt=(
            f"A player has a {fmt_money(bet)} HORN bet "
            f"({fmt_money(Decimal(units))} each on 2, 3, 11, 12) and the "
            f"shooter rolls a {roll}. What is the NET payout?"
        ),
        answer=win,
        explanation=(
            f"The {roll} part ({fmt_money(Decimal(units))}) pays {odds}:1 = "
            f"{fmt_money(Decimal(units) * odds)}, and the other three parts "
            f"({fmt_money(Decimal(3 * units))}) lose: net {fmt_money(win)}."
        ),
    )


def c_and_e_question(rng: random.Random) -> Question:
    units = rng.choice([1, 2, 5])
    bet = Decimal(2 * units)  # split between Craps and Eleven
    if rng.random() < 0.5:
        roll, odds, part = "craps (a 2)", 7, "Craps"
    else:
        roll, odds, part = "an 11", 15, "Eleven"
    win = Decimal(units) * odds - Decimal(units)
    return Question(
        prompt=(
            f"A player has {fmt_money(bet)} C & E "
            f"({fmt_money(Decimal(units))} on Any Craps, "
            f"{fmt_money(Decimal(units))} on the Eleven) and the shooter "
            f"rolls {roll}. What is the NET payout?"
        ),
        answer=win,
        explanation=(
            f"The {part} half pays {odds}:1 = "
            f"{fmt_money(Decimal(units) * odds)}; the other half "
            f"({fmt_money(Decimal(units))}) loses: net {fmt_money(win)}."
        ),
    )


def world_question(rng: random.Random) -> Question:
    units = rng.choice([1, 2, 5])
    bet = Decimal(5 * units)  # 2, 3, 11, 12 and Any Seven
    roll = rng.choice([2, 3, 7, 11, 12])
    if roll == 7:
        return Question(
            prompt=(
                f"A player has a {fmt_money(bet)} WORLD bet "
                f"({fmt_money(Decimal(units))} each on 2, 3, 11, 12 and Any "
                "Seven) and the shooter rolls a 7. What is the NET payout?"
            ),
            answer=Decimal(0),
            explanation=(
                "The Any Seven part pays 4:1, exactly covering the four "
                "losing horn parts — the world bet pushes on a 7. Pay $0."
            ),
        )
    odds = 30 if roll in (2, 12) else 15
    win = Decimal(units) * odds - Decimal(4 * units)
    return Question(
        prompt=(
            f"A player has a {fmt_money(bet)} WORLD bet "
            f"({fmt_money(Decimal(units))} each on 2, 3, 11, 12 and Any "
            f"Seven) and the shooter rolls a {roll}. What is the NET payout?"
        ),
        answer=win,
        explanation=(
            f"The {roll} pays {odds}:1 = {fmt_money(Decimal(units) * odds)}; "
            f"the other four parts ({fmt_money(Decimal(4 * units))}) lose: "
            f"net {fmt_money(win)}."
        ),
    )


def make_question(rng: random.Random | None = None) -> Question:
    rng = rng or random.Random()
    generator = rng.choice(
        [hardway_question, hardway_question, one_roll_question,
         one_roll_question, horn_question, c_and_e_question, world_question]
    )
    return generator(rng)
