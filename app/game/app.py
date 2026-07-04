import sys
import time
from multiprocessing import Process, Queue, Value

from app.game.game import run_game_window
from app.hand.camera_window import run_camera_window


def main():
    control_queue = Queue(maxsize=1)
    start_time = Value("d", 0.0)
    stop_time = Value("d", 0.0)

    game_process = Process(
        target=run_game_window,
        args=(control_queue, start_time, stop_time),
        name="GameWindow",
    )
    camera_process = Process(
        target=run_camera_window,
        args=(control_queue, start_time, stop_time),
        name="CameraWindow",
    )

    start_time.value = time.monotonic()  # 起動前に確定させる
    game_process.start()
    camera_process.start()

    try:
        game_process.join()
    finally:
        stop_time.value = time.monotonic()
        camera_process.join(timeout=3)
        if camera_process.is_alive():
            camera_process.terminate()
            camera_process.join(timeout=2)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
