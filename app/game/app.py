# game/app.py
"""game/app.py

Launch the hand camera window (separate process, produces hand-based
control via a queue) and the pygame game window (main process)
together.

Run with: python -m game.app
"""

import sys
from multiprocessing import Event, Process, Queue

from app.game.game import run_game_window
from app.hand.camera_window import run_camera_window


def main():
    control_queue = Queue(maxsize=1)
    stop_event = Event()

    camera_process = Process(
        target=run_camera_window,
        args=(control_queue, stop_event),
        name="CameraWindow",
    )
    camera_process.start()

    try:
        run_game_window(control_queue)
    finally:
        stop_event.set()
        camera_process.join(timeout=3)
        if camera_process.is_alive():
            camera_process.terminate()
            camera_process.join(timeout=2)


if __name__ == "__main__":
    sys.exit(main())