# app/game/input.py
"""Pure input-combination logic: camera/hand control + keyboard flags
-> unified directional intent + normalized speed vector.

No pygame dependency here. The caller (game.py) is responsible for
converting raw pygame key state into a plain dict before calling
compute_input().
"""

import csv
import os
from time import time

MOVEMENT_CSV_PATH = "app/data/movement.csv"


def _ensure_csv_header(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "dx_cm", "ax", "right", "left"])


def log_cm(cm, ax, right, left, path=MOVEMENT_CSV_PATH):
    _ensure_csv_header(path)
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([time(), cm, ax, right, left])


from app.config import (
    WASD,
    DEADZONE_CM,
    HAND_INPUT_METHOD,
    MAX_HAND_SPEED,
    MAX_HAND_ACC,
    WINDOW_W,
    WINDOW_H,
    FLICK_ACCELERATION,
)
from app.hand.gesture import HandGesture


def _direction_from_position(dx_cm, dy_cm):
    x_dir = 0
    y_dir = 0
    if dx_cm > DEADZONE_CM:
        x_dir = 1
    elif dx_cm < -DEADZONE_CM:
        x_dir = -1

    if dy_cm > DEADZONE_CM:
        y_dir = 1
    elif dy_cm < -DEADZONE_CM:
        y_dir = -1

    return x_dir, y_dir


def _normalize_keys(keys):
    if not keys:
        return False, False, False, False

    up = bool(keys.get("up") or keys.get("w"))
    down = bool(keys.get("down") or keys.get("s"))
    left = bool(keys.get("left") or keys.get("a"))
    right = bool(keys.get("right") or keys.get("d"))
    return up, down, left, right


# --- Flick detection: simple acceleration threshold, no averaging ---

_flick_dir = 0  # -1 / 0 / +1, holds until FIST resets it
_last_sx = 0.0
_last_time = time()


def _update_flick(ax):
    global _flick_dir
    if abs(ax) >= FLICK_ACCELERATION and abs(ax) < 200:
        _flick_dir = 1 if ax < 0 else -1
    return _flick_dir


def reset_flick_state():
    """Clear flick lock (e.g. on FIST or round reset)."""
    global _flick_dir, _last_sx, _last_time
    _flick_dir = 0
    _last_sx = 0.0
    _last_time = time()


def compute_input(control, keys=None):
    """Convert hand-control + (optional) keyboard input into unified
    directional input flags AND a normalized speed vector.

    Returns a dict with up/down/left/right flags, vx (normalized speed,
    -1..1), want_jump, state, and relative_cm.
    """
    global _last_sx, _last_time

    state = control["state"]
    dx_cm, dy_cm = control["relative_cm"]

    x_dir, y_dir = _direction_from_position(dx_cm, dy_cm)

    right = x_dir == 1
    left = x_dir == -1
    down = y_dir == 1
    up = y_dir == -1

    flick_dir = 0
    ax = 0.0

    if state == HandGesture.FIST:
        up = down = left = right = False
        reset_flick_state()
    elif state == HandGesture.OPEN:
        up = True
        down = False

    key_up, key_down, key_left, key_right = _normalize_keys(keys)
    up = up or key_up
    down = down or key_down
    left = left or key_left
    right = right or key_right

    # --- Normalized horizontal speed intent ---
    if "speed" in control:
        sx, _sy = control["speed"]
        now = time()
        dt = now - _last_time

        if HAND_INPUT_METHOD == "speed":
            vx = max(-1.0, min(1.0, sx / MAX_HAND_SPEED))
        elif HAND_INPUT_METHOD == "acceleration":
            ax = (sx - _last_sx) / dt if dt > 0 else 0.0
            flick_dir = _update_flick(ax) if state != HandGesture.FIST else 0
            vx = float(flick_dir)
            _last_sx = sx
        else:
            vx = 0.0

        _last_time = now
    else:
        # "distance" mode (or no speed data): derive from flags.
        vx = 0.0
        if right and not left:
            vx = 1.0
        elif left and not right:
            vx = -1.0

    # Keep left/right flags consistent with the flick lock.
    if flick_dir == 1:
        right, left = True, False
    elif flick_dir == -1:
        left, right = True, False

    # Keyboard overrides/adds to vx as full-speed intent.
    if key_right and not key_left:
        vx = 1.0
    elif key_left and not key_right:
        vx = -1.0

    log_cm(dx_cm, ax, right, left)
    return {
        "up": up,
        "down": down,
        "left": left,
        "right": right,
        "vx": vx,
        "want_jump": up,
        "state": state,
        "relative_cm": (dx_cm, dy_cm),
    }
