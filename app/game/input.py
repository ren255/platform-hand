# app/game/input.py
from app.config import WASD
from app.hand.gesture import HandGesture
from app.config import DEADZONE_CM

def _direction_from_position(dx_cm, dy_cm):
    """Return horizontal/vertical direction flags from relative hand position.
    """
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
    """Normalize the keyboard input into up/down/left/right booleans.

    `keys` may be:
      - None: no keyboard input.
      - a dict with any of "up"/"down"/"left"/"right" (and/or "w"/"a"/"s"/"d")
        boolean keys.
    Anything not present defaults to False.
    """
    if not keys:
        return False, False, False, False

    up = bool(keys.get("up") or keys.get("w"))
    down = bool(keys.get("down") or keys.get("s"))
    left = bool(keys.get("left") or keys.get("a"))
    right = bool(keys.get("right") or keys.get("d"))
    return up, down, left, right


def compute_input(control, keys=None):
    """Convert hand-control + (optional) game-window keyboard input into
    unified directional input flags.

    Args:
        control: dict from the hand/camera process with:
            - "state": HandGesture
            - "relative_cm": (dx_cm, dy_cm)
        keys: optional dict of keyboard flags from the game window, e.g.
            {"up": bool, "down": bool, "left": bool, "right": bool}
            (or "w"/"a"/"s"/"d" equivalents). Hand input and keyboard input
            are OR-combined, so either source can drive movement.

    Returns a dict with keys:
      - up, down, left, right: combined directional flags (hand + WASD
        gesture overrides + game-window keyboard, all OR-combined with
        the mutual-exclusion rules below).
      - state: the HandGesture used
      - relative_cm: (dx, dy) from the control dict
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

    # Combine in the game-window keyboard input (OR-combined with hand input).
    key_up, key_down, key_left, key_right = _normalize_keys(keys)
    up = up or key_up
    down = down or key_down
    left = left or key_left
    right = right or key_right

    # S/W and A/D are mutually exclusive. Key state wins on conflict.

    return {
        "up": up,
        "down": down,
        "left": left,
        "right": right,
        "state": state,
        "relative_cm": (dx_cm, dy_cm),
    }