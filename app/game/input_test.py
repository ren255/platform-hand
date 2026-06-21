import time
from multiprocessing import Event, Process, Queue

from app.game.input import compute_input
from app.hand.camera_window import run_camera_window


def _format_input(input_dict):
    """Return a compact string for the directional/WASD flags."""
    action = ""
    if input_dict["up"]:
        action += "U"
    if input_dict["down"]:
        action += "D"
    if input_dict["left"]:
        action += "L"
    if input_dict["right"]:
        action += "R"
    if not action:
        action = "-"

    return f"action={action}"


def main():
    """Launch the hand-controller window and log right-hand state + input flags."""
    control_queue = Queue(maxsize=1)
    stop_event = Event()

    process = Process(
        target=run_camera_window,
        args=(control_queue, stop_event),
        name="CameraWindow",
    )
    process.start()

    print("Logging right hand state + input. Press Ctrl+C to stop.")
    try:
        while True:
            try:
                control = control_queue.get(timeout=0.1)
            except Exception:
                continue

            input_dict = compute_input(control)
            state = input_dict["state"]
            dx_cm, dy_cm = input_dict["relative_cm"]
            print(
                f"[Right hand] state={state.name}, "
                f"relative=(x={dx_cm:+.2f}cm, y={dy_cm:+.2f}cm), "
                f"{_format_input(input_dict)}"
            )
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stop_event.set()
        process.join(timeout=3)
        if process.is_alive():
            process.terminate()
            process.join(timeout=2)


if __name__ == "__main__":
    main()
