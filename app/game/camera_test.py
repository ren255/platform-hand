# game/camera_test.py
"""game/camera_test.py

Launch ONLY the hand camera window, for isolated testing of camera/hand
detection without the game window.

Run with: python -m game.camera_test
"""

import sys
from multiprocessing import Event, Process, Queue

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
        # Drain the queue and print incoming control data so the camera
        # process can be exercised standalone (Ctrl+C to stop).
        while True:
            try:
                control = control_queue.get(timeout=1)
                print(control)
            except Exception:
                pass
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        camera_process.join(timeout=3)
        if camera_process.is_alive():
            camera_process.terminate()
            camera_process.join(timeout=2)


if __name__ == "__main__":
    sys.exit(main())