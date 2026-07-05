"""Interactive menu for the casino dealer training simulator.

Run with:  python -m dealer_trainer
"""

from __future__ import annotations

import random
import sys

from . import baccarat, blackjack, craps, craps_props, roulette
from .quiz import run_drill

DRILLS = {
    "1": ("Blackjack — payouts, insurance & soft totals", blackjack.make_question),
    "2": ("Craps — base dealing payouts", craps.make_question),
    "3": ("Craps — proposition (center) payouts", craps_props.make_question),
    "4": ("Roulette — payouts", roulette.make_question),
    "5": ("Baccarat — banker commission", baccarat.make_question),
}

BANNER = r"""
  ____             _             _____          _
 |  _ \  ___  __ _| | ___ _ __  |_   _| __ __ _(_)_ __   ___ _ __
 | | | |/ _ \/ _` | |/ _ \ '__|   | || '__/ _` | | '_ \ / _ \ '__|
 | |_| |  __/ (_| | |  __/ |      | || | | (_| | | | | |  __/ |
 |____/ \___|\__,_|_|\___|_|      |_||_|  \__,_|_|_| |_|\___|_|

            Casino Dealer Training Simulator
"""


def ask_num_questions(default: int = 10) -> int:
    raw = input(f"How many questions? [{default}] ").strip()
    if not raw:
        return default
    try:
        return max(1, min(100, int(raw)))
    except ValueError:
        return default


def main() -> int:
    rng = random.Random()
    print(BANNER)
    while True:
        print("\nChoose a drill:")
        for key, (title, _) in DRILLS.items():
            print(f"  {key}. {title}")
        print("  6. Mixed — questions from every game")
        print("  0. Quit")
        choice = input("> ").strip().lower()

        if choice in ("0", "q", "quit", "exit"):
            print("Good luck on the floor!")
            return 0
        if choice == "6":
            makers = [maker for _, maker in DRILLS.values()]
            n = ask_num_questions()
            run_drill("Mixed drill — all games",
                      lambda: rng.choice(makers)(rng), n)
        elif choice in DRILLS:
            title, maker = DRILLS[choice]
            n = ask_num_questions()
            run_drill(title, lambda: maker(rng), n)
        else:
            print("Please pick an option from the menu.")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nGood luck on the floor!")
        sys.exit(0)
