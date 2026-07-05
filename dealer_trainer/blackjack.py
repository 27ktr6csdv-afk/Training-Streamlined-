"""Blackjack dealer drill: payouts, insurance logic, and soft-hand totals.

Every question displays a player's hand and the dealer's upcard, then quizzes
the trainee on one of:

* the correct payout (blackjack pays 3:2, standard wins pay even money),
* insurance logic (offered on an ace, max half the bet, pays 2:1, even money),
* reading the hand total and calling it soft or hard.
"""

from __future__ import annotations

import random
from decimal import Decimal

from .quiz import Question, fmt_money

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["♠", "♥", "♦", "♣"]  # spade heart diamond club

BLACKJACK_MULTIPLIER = Decimal("1.5")  # 3:2

# Bets chosen so every 3:2 payout lands on a real chip amount.
BET_SIZES = [Decimal(b) for b in (10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 150, 200)]


def card_value(rank: str) -> int:
    if rank == "A":
        return 11
    if rank in ("J", "Q", "K"):
        return 10
    return int(rank)


def hand_total(ranks: list[str]) -> tuple[int, bool]:
    """Return (best total, is_soft).

    A hand is soft when an ace is currently counted as 11.
    """
    total = sum(card_value(r) for r in ranks)
    aces_as_eleven = sum(1 for r in ranks if r == "A")
    while total > 21 and aces_as_eleven:
        total -= 10
        aces_as_eleven -= 1
    return total, aces_as_eleven > 0


def deal_card(rng: random.Random) -> str:
    return f"{rng.choice(RANKS)}{rng.choice(SUITS)}"


def show_hand(cards: list[str]) -> str:
    return "  ".join(cards)


def rank_of(card: str) -> str:
    return card[:-1]


def _table(player: list[str], upcard: str) -> str:
    return (
        f"  Dealer upcard : {upcard}  [hole card face down]\n"
        f"  Player hand   : {show_hand(player)}"
    )


def _deal_hand(rng: random.Random, size: int = 2) -> list[str]:
    return [deal_card(rng) for _ in range(size)]


def _deal_blackjack(rng: random.Random) -> list[str]:
    ace = f"A{rng.choice(SUITS)}"
    ten = f"{rng.choice(['10', 'J', 'Q', 'K'])}{rng.choice(SUITS)}"
    cards = [ace, ten]
    rng.shuffle(cards)
    return cards


def _deal_soft_hand(rng: random.Random) -> list[str]:
    """Deal a 2-3 card hand guaranteed to contain at least one ace."""
    cards = [f"A{rng.choice(SUITS)}"]
    cards.extend(_deal_hand(rng, rng.choice([1, 1, 2])))
    rng.shuffle(cards)
    total, _ = hand_total([rank_of(c) for c in cards])
    if total > 21:  # busted practice hands are useless; redeal
        return _deal_soft_hand(rng)
    return cards


def payout_question(rng: random.Random) -> Question:
    bet = rng.choice(BET_SIZES)
    if rng.random() < 0.5:
        # Player blackjack, dealer upcard is not an ace and dealer has no BJ.
        player = _deal_blackjack(rng)
        upcard = deal_card(rng)
        while rank_of(upcard) == "A":
            upcard = deal_card(rng)
        win = bet * BLACKJACK_MULTIPLIER
        return Question(
            prompt=(
                f"{_table(player, upcard)}\n"
                f"  Player's bet  : {fmt_money(bet)}\n"
                "The player has blackjack and the dealer does not. "
                "How much do you PAY the player (winnings only, not the bet)?"
            ),
            answer=win,
            explanation=(
                f"Blackjack pays 3:2 — {fmt_money(bet)} x 1.5 = {fmt_money(win)}. "
                "The original bet stays with the player."
            ),
        )
    # Standard winning hand, even money.
    while True:
        player = _deal_hand(rng)
        total, _ = hand_total([rank_of(c) for c in player])
        if total < 21:
            break
    upcard = deal_card(rng)
    return Question(
        prompt=(
            f"{_table(player, upcard)}\n"
            f"  Player's bet  : {fmt_money(bet)}\n"
            f"The player stands on {total} and the dealer busts. "
            "How much do you PAY the player?"
        ),
        answer=bet,
        explanation=f"Standard wins pay even money (1:1): pay {fmt_money(bet)}.",
    )


def insurance_question(rng: random.Random) -> Question:
    bet = rng.choice(BET_SIZES)
    player = _deal_hand(rng)
    upcard = f"A{rng.choice(SUITS)}"
    max_insurance = bet / 2
    style = rng.choice(["max", "pays", "loses", "even_money", "when"])

    if style == "max":
        return Question(
            prompt=(
                f"{_table(player, upcard)}\n"
                f"  Player's bet  : {fmt_money(bet)}\n"
                "The dealer shows an ace and calls 'insurance'. What is the "
                "MAXIMUM insurance bet this player may make?"
            ),
            answer=max_insurance,
            explanation=(
                "Insurance is limited to half the original wager: "
                f"{fmt_money(bet)} / 2 = {fmt_money(max_insurance)}."
            ),
        )
    if style == "pays":
        win = max_insurance * 2
        return Question(
            prompt=(
                f"{_table(player, upcard)}\n"
                f"  Player's bet  : {fmt_money(bet)}   "
                f"Insurance bet: {fmt_money(max_insurance)}\n"
                "The dealer turns over a ten — blackjack. How much do you PAY "
                "on the insurance bet (winnings only)?"
            ),
            answer=win,
            explanation=(
                "Insurance pays 2:1: "
                f"{fmt_money(max_insurance)} x 2 = {fmt_money(win)}. "
                "The player's main bet loses (unless they also have blackjack, "
                "which pushes)."
            ),
        )
    if style == "loses":
        return Question(
            prompt=(
                f"{_table(player, upcard)}\n"
                f"  Player's bet  : {fmt_money(bet)}   "
                f"Insurance bet: {fmt_money(max_insurance)}\n"
                "The dealer checks and does NOT have blackjack. What do you do "
                "with the insurance bet? (pay it / take it / push)"
            ),
            answer="take it",
            accept=("take", "collect", "collect it", "it loses", "loses",
                    "take the bet"),
            explanation=(
                "No dealer blackjack means insurance loses — collect the "
                "insurance bet and play the hand out normally."
            ),
        )
    if style == "even_money":
        player = _deal_blackjack(rng)
        return Question(
            prompt=(
                f"{_table(player, upcard)}\n"
                f"  Player's bet  : {fmt_money(bet)}\n"
                "The player has blackjack, the dealer shows an ace, and the "
                "player asks for EVEN MONEY. How much do you pay?"
            ),
            answer=bet,
            explanation=(
                "Even money pays the blackjack at 1:1 immediately "
                f"({fmt_money(bet)}), before the dealer checks the hole card. "
                "It is mathematically identical to insuring a blackjack."
            ),
        )
    return Question(
        prompt=(
            f"{_table(player, upcard)}\n"
            "Which dealer upcard requires you to offer insurance? "
            "(name the card)"
        ),
        answer="ace",
        accept=("a", "an ace", "ace up", "aces"),
        explanation="Insurance is offered only when the dealer's upcard is an ace.",
    )


def soft_total_question(rng: random.Random) -> Question:
    if rng.random() < 0.6:
        player = _deal_soft_hand(rng)
    else:
        while True:
            player = _deal_hand(rng, rng.choice([2, 2, 3]))
            total, _ = hand_total([rank_of(c) for c in player])
            if total <= 21:
                break
    upcard = deal_card(rng)
    total, soft = hand_total([rank_of(c) for c in player])
    label = "soft" if soft else "hard"
    return Question(
        prompt=(
            f"{_table(player, upcard)}\n"
            "Call this hand's total, e.g. 'soft 17' or 'hard 12'."
        ),
        answer=f"{label} {total}",
        accept=(f"{label}{total}", f"{label[0]}{total}", f"{total} {label}"),
        explanation=(
            f"An ace counting as 11 makes the hand soft. This hand is "
            f"{label} {total}."
            if soft
            else f"No ace is counting as 11 here, so the hand is hard {total}."
        ),
    )


def make_question(rng: random.Random | None = None) -> Question:
    rng = rng or random.Random()
    generator = rng.choice(
        [payout_question, insurance_question, soft_total_question]
    )
    return generator(rng)
