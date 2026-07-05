"""Baccarat commission drill.

In classic (commission) baccarat, winning BANKER bets pay even money less a
5% commission. Most houses pay the win in full and track the commission with
lammers in the commission box, collecting it at the end of the shoe or when
the player colors up. This drill covers:

* figuring 5% commission on a single banker win,
* the net result of a banker win,
* totaling commission owed across several wins in a shoe.
"""

from __future__ import annotations

import random
from decimal import Decimal

from .quiz import Question, fmt_money

# Bets chosen so 5% commission lands on real chip amounts.
BANKER_BETS = [Decimal(b) for b in
               (20, 25, 40, 50, 60, 80, 100, 120, 200, 300, 500, 1000)]

COMMISSION = Decimal("0.05")


def commission_question(rng: random.Random) -> Question:
    bet = rng.choice(BANKER_BETS)
    vig = bet * COMMISSION
    return Question(
        prompt=(
            f"A player has {fmt_money(bet)} on BANKER and banker wins the "
            "hand. How much commission do you mark for this win?"
        ),
        answer=vig,
        explanation=(
            f"Commission is 5% of the winning banker bet: "
            f"{fmt_money(bet)} x 0.05 = {fmt_money(vig)}."
        ),
    )


def net_payout_question(rng: random.Random) -> Question:
    bet = rng.choice(BANKER_BETS)
    vig = bet * COMMISSION
    net = bet - vig
    if rng.random() < 0.5:
        return Question(
            prompt=(
                f"A player has {fmt_money(bet)} on BANKER and banker wins. "
                "The house collects commission immediately instead of using "
                "lammers. How much do you pay the player?"
            ),
            answer=net,
            explanation=(
                f"Banker pays even money less 5%: {fmt_money(bet)} - "
                f"{fmt_money(vig)} = {fmt_money(net)}."
            ),
        )
    return Question(
        prompt=(
            f"A player has {fmt_money(bet)} on BANKER and banker wins. Your "
            "house pays the win in full and marks the commission with "
            "lammers. How much do you PAY the player right now?"
        ),
        answer=bet,
        explanation=(
            f"Pay the win in full ({fmt_money(bet)}) and place "
            f"{fmt_money(vig)} in lammers in this player's commission box — "
            "it is collected at the end of the shoe."
        ),
    )


def shoe_total_question(rng: random.Random) -> Question:
    wins = [rng.choice(BANKER_BETS) for _ in range(rng.choice([3, 4, 5]))]
    total_vig = sum(w * COMMISSION for w in wins)
    wins_text = ", ".join(fmt_money(w) for w in wins)
    parts = " + ".join(fmt_money(w * COMMISSION) for w in wins)
    return Question(
        prompt=(
            "The shoe is over and a player is coloring up. During the shoe "
            f"they won banker bets of: {wins_text}. "
            "How much commission do you collect?"
        ),
        answer=total_vig,
        explanation=(
            f"5% of each winning banker bet: {parts} = {fmt_money(total_vig)}."
        ),
    )


def player_bet_question(rng: random.Random) -> Question:
    bet = rng.choice(BANKER_BETS)
    return Question(
        prompt=(
            f"A player has {fmt_money(bet)} on PLAYER and player wins the "
            "hand. How much do you pay, and is any commission owed? "
            "(answer with the dollar amount)"
        ),
        answer=bet,
        explanation=(
            f"Winning PLAYER bets pay even money ({fmt_money(bet)}) with NO "
            "commission — the 5% applies only to winning banker bets."
        ),
    )


def make_question(rng: random.Random | None = None) -> Question:
    rng = rng or random.Random()
    generator = rng.choice(
        [commission_question, commission_question, net_payout_question,
         shoe_total_question, player_bet_question]
    )
    return generator(rng)
