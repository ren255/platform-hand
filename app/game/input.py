# app/game/input.py
"""Pure input-combination logic: camera/hand control + keyboard flags
-> unified directional intent + normalized speed vector.

No pygame dependency here. The caller (game.py) is responsible for
converting raw pygame key state into a plain dict before calling
compute_input().
"""

from app.config import WASD, DEADZONE_CM, HAND_INPUT_METHOD, MAX_HAND_SPEED
from app.hand.gesture import HandGesture


def _direction_from_position(dx_cm, dy_cm):
    """Return horizontal/vertical direction flags from relative hand position."""
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
    """Normalize a plain keyboard-flags dict into up/down/left/right booleans.

    `keys` may be:
      - None: no keyboard input.
      - a dict with any of "up"/"down"/"left"/"right" (and/or "w"/"a"/"s"/"d")
        boolean keys. Anything not present defaults to False.
    """
    if not keys:
        return False, False, False, False

    up = bool(keys.get("up") or keys.get("w"))
    down = bool(keys.get("down") or keys.get("s"))
    left = bool(keys.get("left") or keys.get("a"))
    right = bool(keys.get("right") or keys.get("d"))
    return up, down, left, right


def compute_input(control, keys=None):
    """Convert hand-control + (optional) keyboard input into unified
    directional input flags AND a normalized speed vector.

    Args:
        control: dict from the hand/camera process with:
            - "state": HandGesture
            - "relative_cm": (dx_cm, dy_cm)
            - "speed": optional (sx, sy), only present in "speed" mode
        keys: optional plain dict of keyboard flags, e.g.
            {"up": bool, "down": bool, "left": bool, "right": bool}
            (or "w"/"a"/"s"/"d" equivalents). Hand input and keyboard
            input are OR-combined for flags.

    Returns a dict with keys:
      - up, down, left, right: combined directional intent flags.
      - vx: normalized horizontal speed intent in [-1.0, 1.0].
      - want_jump: bool, True if "up" intent is currently active.
      - state: the HandGesture used.
      - relative_cm: (dx, dy) from the control dict.

    Notes:
      - This module only expresses *intent*. Whether a jump is actually
        allowed (on_ground) and how gravity/collisions apply is entirely
        up to game.py. This keeps physics state out of input.py.
    """
    state = control["state"]
    dx_cm, dy_cm = control["relative_cm"]

    x_dir, y_dir = _direction_from_position(dx_cm, dy_cm)

    # Arrow-style directions from hand position.
    right = x_dir == 1
    left = x_dir == -1
    down = y_dir == 1
    up = y_dir == -1

    if state == HandGesture.FIST:
        up = down = left = right = False
    elif state == HandGesture.OPEN:
        up = True
        down = False

    # Combine in keyboard input (OR-combined with hand input).
    key_up, key_down, key_left, key_right = _normalize_keys(keys)
    up = up or key_up
    down = down or key_down
    left = left or key_left
    right = right or key_right

    # --- Normalized horizontal speed intent ---
    if HAND_INPUT_METHOD == "speed" and "speed" in control:
        sx, _sy = control["speed"]
        vx = max(-1.0, min(1.0, sx / MAX_HAND_SPEED))
    else:
        # "distance" mode (or no speed data): derive from flags.
        vx = 0.0
        if right and not left:
            vx = 1.0
        elif left and not right:
            vx = -1.0

    # Keyboard overrides/adds to vx as full-speed intent.
    if key_right and not key_left:
        vx = 1.0
    elif key_left and not key_right:
        vx = -1.0

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