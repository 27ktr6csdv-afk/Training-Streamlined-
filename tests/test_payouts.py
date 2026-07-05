"""Sanity checks for the dealer trainer's payout math and answer parsing."""

import random
import unittest
from decimal import Decimal

from dealer_trainer import baccarat, blackjack, craps, craps_props, roulette
from dealer_trainer.blackjack import hand_total
from dealer_trainer.quiz import Question, fmt_money, is_correct, parse_money


class TestQuizEngine(unittest.TestCase):
    def test_parse_money(self):
        self.assertEqual(parse_money("$37.50"), Decimal("37.50"))
        self.assertEqual(parse_money("37.5"), Decimal("37.5"))
        self.assertEqual(parse_money(" $1,250 "), Decimal("1250"))
        self.assertIsNone(parse_money("abc"))
        self.assertIsNone(parse_money(""))

    def test_fmt_money(self):
        self.assertEqual(fmt_money(Decimal("40")), "$40")
        self.assertEqual(fmt_money(Decimal("37.5")), "$37.50")
        self.assertEqual(fmt_money(Decimal("1250")), "$1,250")

    def test_money_answers_match_regardless_of_format(self):
        q = Question(prompt="", answer=Decimal("37.50"))
        for response in ("37.5", "$37.50", " 37.50 "):
            self.assertTrue(is_correct(q, response))
        self.assertFalse(is_correct(q, "38"))

    def test_text_answers_accept_variants(self):
        q = Question(prompt="", answer="soft 17", accept=("s17", "soft17"))
        self.assertTrue(is_correct(q, "Soft 17"))
        self.assertTrue(is_correct(q, "  s17 "))
        self.assertFalse(is_correct(q, "hard 17"))


class TestBlackjack(unittest.TestCase):
    def test_hand_totals(self):
        self.assertEqual(hand_total(["A", "6"]), (17, True))       # soft 17
        self.assertEqual(hand_total(["A", "6", "10"]), (17, False))  # hard 17
        self.assertEqual(hand_total(["A", "A", "9"]), (21, True))
        self.assertEqual(hand_total(["10", "9"]), (19, False))
        self.assertEqual(hand_total(["A", "K"]), (21, True))

    def test_blackjack_pays_three_to_two(self):
        rng = random.Random(7)
        for _ in range(200):
            q = blackjack.payout_question(rng)
            if "blackjack" in q.prompt:
                bet = self._bet_from_prompt(q.prompt)
                self.assertEqual(q.answer, bet * Decimal("1.5"))
            else:
                self.assertEqual(q.answer, self._bet_from_prompt(q.prompt))

    @staticmethod
    def _bet_from_prompt(prompt: str) -> Decimal:
        for line in prompt.splitlines():
            if "Player's bet" in line:
                return parse_money(line.split(":")[1].split()[0])
        raise AssertionError("no bet line in prompt")


class TestGenerators(unittest.TestCase):
    """Every generator must produce answerable questions with exact answers."""

    def test_all_generators_run_clean(self):
        rng = random.Random(42)
        for module in (blackjack, craps, craps_props, roulette, baccarat):
            for _ in range(300):
                q = module.make_question(rng)
                self.assertTrue(q.prompt)
                if isinstance(q.answer, Decimal):
                    # Payouts must land on cents (real chip amounts).
                    self.assertEqual(
                        q.answer, q.answer.quantize(Decimal("0.01")),
                        msg=f"{module.__name__}: {q.prompt} -> {q.answer}",
                    )
                    self.assertGreaterEqual(q.answer, 0)
                else:
                    self.assertTrue(q.answer.strip())


class TestCrapsMath(unittest.TestCase):
    def test_world_pushes_on_seven(self):
        rng = random.Random(1)
        saw_push = False
        for _ in range(200):
            q = craps_props.world_question(rng)
            if "rolls a 7" in q.prompt:
                saw_push = True
                self.assertEqual(q.answer, Decimal(0))
        self.assertTrue(saw_push)


class TestBaccarat(unittest.TestCase):
    def test_commission_is_five_percent(self):
        rng = random.Random(3)
        for _ in range(100):
            q = baccarat.commission_question(rng)
            bet = parse_money(
                q.prompt.split("has ")[1].split(" on BANKER")[0]
            )
            self.assertEqual(q.answer, bet * Decimal("0.05"))


if __name__ == "__main__":
    unittest.main()
