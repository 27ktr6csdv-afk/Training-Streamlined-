"""Craps base-dealing drill: line bets, odds, place bets, field, and buy bets.

House rules used here (the most common Las Vegas schedule):

* Pass / Don't Pass / Come / Don't Come pay even money.
* True odds: 4 & 10 pay 2:1, 5 & 9 pay 3:2, 6 & 8 pay 6:5.
* Place bets: 4 & 10 pay 9:5, 5 & 9 pay 7:5, 6 & 8 pay 7:6.
* Field: 3, 4, 9, 10, 11 pay even money; 2 pays double; 12 pays triple.
* Buy 4 or 10: paid at true odds 2:1, less a 5% commission on the bet.
"""

from __future__ import annotations

import random
from decimal import Decimal
from fractions import Fraction

from .quiz import Question, fmt_money

TRUE_ODDS = {4: Fraction(2, 1), 10: Fraction(2, 1),
             5: Fraction(3, 2), 9: Fraction(3, 2),
             6: Fraction(6, 5), 8: Fraction(6, 5)}

PLACE_ODDS = {4: Fraction(9, 5), 10: Fraction(9, 5),
              5: Fraction(7, 5), 9: Fraction(7, 5),
              6: Fraction(7, 6), 8: Fraction(7, 6)}

# Proper bet units so payouts land on whole/half dollars.
PLACE_UNITS = {4: 5, 10: 5, 5: 5, 9: 5, 6: 6, 8: 6}
ODDS_UNITS = {4: 5, 10: 5, 5: 2, 9: 2, 6: 5, 8: 5}

FIELD_NUMBERS = {2: 2, 3: 1, 4: 1, 9: 1, 10: 1, 11: 1, 12: 3}

LINE_BETS = [Decimal(b) for b in (5, 10, 15, 25, 30, 50, 75, 100)]


def _pay(bet: Decimal, odds: Fraction) -> Decimal:
    return bet * odds.numerator / odds.denominator


def _odds_str(odds: Fraction) -> str:
    return f"{odds.numerator}:{odds.denominator}"


def line_question(rng: random.Random) -> Question:
    bet = rng.choice(LINE_BETS)
    kind, roll = rng.choice(
        [("pass line", "the shooter rolls a 7 on the come-out"),
         ("pass line", "the point is 6 and the shooter rolls a 6"),
         ("don't pass", "the shooter rolls a 3 on the come-out"),
         ("come", "the come point is 9 and the shooter repeats the 9"),
         ("don't come", "the don't come point is 4 and the shooter sevens out")]
    )
    return Question(
        prompt=(
            f"A player has {fmt_money(bet)} on the {kind.upper()} and {roll}. "
            "How much do you pay?"
        ),
        answer=bet,
        explanation=(
            f"All flat line bets (pass, don't pass, come, don't come) pay "
            f"even money: {fmt_money(bet)}."
        ),
    )


def odds_question(rng: random.Random) -> Question:
    point = rng.choice(list(TRUE_ODDS))
    unit = ODDS_UNITS[point]
    bet = Decimal(unit * rng.choice([1, 2, 3, 4, 5, 6, 10]))
    odds = TRUE_ODDS[point]
    win = _pay(bet, odds)
    return Question(
        prompt=(
            f"The point is {point}. A player has {fmt_money(bet)} in ODDS "
            f"behind their pass line bet, and the shooter rolls the {point}. "
            "How much do you pay on the odds?"
        ),
        answer=win,
        explanation=(
            f"Odds on the {point} pay true odds of {_odds_str(odds)}: "
            f"{fmt_money(bet)} pays {fmt_money(win)}."
        ),
    )


def place_question(rng: random.Random) -> Question:
    number = rng.choice(list(PLACE_ODDS))
    unit = PLACE_UNITS[number]
    bet = Decimal(unit * rng.choice([1, 2, 3, 4, 5, 6, 10]))
    odds = PLACE_ODDS[number]
    win = _pay(bet, odds)
    return Question(
        prompt=(
            f"A player has {fmt_money(bet)} PLACED on the {number} and the "
            f"shooter rolls a {number}. How much do you pay?"
        ),
        answer=win,
        explanation=(
            f"Place bets on the {number} pay {_odds_str(odds)}: "
            f"{fmt_money(bet)} pays {fmt_money(win)}."
        ),
    )


def field_question(rng: random.Random) -> Question:
    bet = rng.choice(LINE_BETS)
    roll = rng.choice(list(FIELD_NUMBERS))
    multiplier = FIELD_NUMBERS[roll]
    win = bet * multiplier
    if multiplier == 1:
        detail = f"The field pays even money on a {roll}"
    elif multiplier == 2:
        detail = "The 2 pays double in the field"
    else:
        detail = "The 12 pays triple in the field (house rule; some pay double)"
    return Question(
        prompt=(
            f"A player has {fmt_money(bet)} in the FIELD and the shooter "
            f"rolls a {roll}. How much do you pay?"
        ),
        answer=win,
        explanation=f"{detail}: {fmt_money(bet)} pays {fmt_money(win)}.",
    )


def buy_question(rng: random.Random) -> Question:
    number = rng.choice([4, 10])
    bet = Decimal(rng.choice([20, 25, 40, 50, 100]))
    vig = (bet * Decimal("0.05")).quantize(Decimal("0.01"))
    win = bet * 2
    return Question(
        prompt=(
            f"A player BUYS the {number} for {fmt_money(bet)} (commission "
            f"already collected) and the shooter rolls the {number}. "
            "How much do you pay?"
        ),
        answer=win,
        explanation=(
            f"Buy bets pay true odds — 2:1 on the {number} — so "
            f"{fmt_money(bet)} pays {fmt_money(win)}. The house keeps the 5% "
            f"commission of {fmt_money(vig)}."
        ),
    )


def make_question(rng: random.Random | None = None) -> Question:
    rng = rng or random.Random()
    generator = rng.choice(
        [line_question, odds_question, odds_question,
         place_question, place_question, field_question, buy_question]
    )
    return generator(rng)
