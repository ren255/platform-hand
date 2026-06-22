# game/game_test.py
"""game/game_test.py

Launch ONLY the game window, for isolated testing of physics/collision
and keyboard input without starting the camera process.

A dummy control_queue (always empty) is passed in, so run_game_window()
falls back to IDLE_CONTROL and only keyboard input drives the square.

Run with: python -m game.game_test
"""

import sys

from app.game.game import run_game_window


def main():
    # No camera process: pass None so game.py skips queue polling entirely
    # and relies solely on keyboard input.
    run_game_window(control_queue=None)


if __name__ == "__main__":
    sys.exit(main())