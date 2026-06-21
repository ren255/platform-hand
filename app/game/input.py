from app.config import WASD
from app.hand.gesture import HandGesture


def _direction_from_position(dx_cm, dy_cm, deadzone_cm=5.0):
    """Return horizontal/vertical direction flags from relative hand position.

    Within +/- deadzone_cm nothing is active. Beyond +deadzone_cm the positive
    direction is active; below -deadzone_cm the negative direction is active.
    """
    x_dir = 0
    y_dir = 0
    if dx_cm > deadzone_cm:
        x_dir = 1
    elif dx_cm < -deadzone_cm:
        x_dir = -1

    if dy_cm > deadzone_cm:
        y_dir = 1
    elif dy_cm < -deadzone_cm:
        y_dir = -1

    return x_dir, y_dir


def _gesture_overrides_w(gesture):
    """These gestures force W on (and override S)."""
    return gesture in {
        HandGesture.OPEN,
        HandGesture.POINTING,
        HandGesture.THUMBS_UP,
    }


def compute_input(control):
    """Convert a control dict into unified directional input flags.

    Returns a dict with keys:
      - up, down, left, right: combined directional flags. When WASD is
        enabled these include the WASD gesture overrides with key priority.
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

    w = a = s = d = False
    if WASD:
        # WASD mapping: W=up, A=left, S=down, D=right.
        w = up
        a = left
        s = down
        d = right

        # Specific gestures force W on and S off regardless of position.
        if _gesture_overrides_w(state):
            w = True
            s = False

        # Combine arrow and WASD, giving WASD key priority.
        up = up or w
        down = down or s
        left = left or a
        right = right or d

        # S/W and A/D are mutually exclusive. Key state wins on conflict.
        if up and down:
            if w and not s:
                down = False
            elif s and not w:
                up = False
            else:
                # Both from position (should not happen); default to up.
                down = False
        if left and right:
            left = False
            right = False

    return {
        "up": up,
        "down": down,
        "left": left,
        "right": right,
        "state": state,
        "relative_cm": (dx_cm, dy_cm),
    }
