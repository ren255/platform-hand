# app/game/input.py
"""Pure input-combination logic: camera/hand control + keyboard flags
-> unified directional intent + normalized speed vector.

No pygame dependency here. The caller (game.py) is responsible for
converting raw pygame key state into a plain dict before calling
compute_input().
"""

from collections import deque
from time import time

from app.config import WASD, DEADZONE_CM, HAND_INPUT_METHOD, MAX_HAND_SPEED, MAX_HAND_ACC
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


# --- Flick-detection state (module-level, persists across calls) ---
_sx_history = deque(maxlen=1)   # past raw sx samples, for moving average
_last_avg_sx = 0.0
_last_time = time()

_FLICK_NONE = 0
_FLICK_GOING = 1
_FLICK_LOCKED = 2

_flick_state = _FLICK_NONE
_flick_dir = 0     # -1 / 0 / +1, meaningful for GOING and LOCKED
_flick_peak = 0.0  # peak |ax_norm| seen during the GOING (outgoing) phase

FLICK_GOING_THRESHOLD = 0.8     # 行きの加速度がこれ以上で「行き」を検出
FLICK_RETURN_RATIO = 0.5        # 戻りの加速度が 行きピーク * この値 以下ならフリック確定


def _moving_average_sx(sx):
    _sx_history.append(sx)
    return sum(_sx_history) / len(_sx_history)


def _update_flick(ax_norm):
    """Update flick state machine from a normalized acceleration value.

    Lock is only released by an opposite-direction flick (handled here)
    or by FIST (handled via reset_flick_state() from compute_input).
    """
    global _flick_state, _flick_dir, _flick_peak

    mag = abs(ax_norm)
    sign = 1 if ax_norm > 0 else (-1 if ax_norm < 0 else 0)

    if _flick_state == _FLICK_NONE:
        if mag >= FLICK_GOING_THRESHOLD:
            _flick_state = _FLICK_GOING
            _flick_dir = sign
            _flick_peak = mag

    elif _flick_state == _FLICK_GOING:
        if sign == _flick_dir:
            # still in the outgoing motion -> track the peak.
            _flick_peak = max(_flick_peak, mag)
        else:
            # motion has reversed (the "return") -> check the condition.
            if mag <= FLICK_RETURN_RATIO * _flick_peak:
                _flick_state = _FLICK_LOCKED
                # _flick_dir stays as the outgoing direction.
            else:
                # not a clean flick -> abandon and start over.
                _flick_state = _FLICK_NONE
                _flick_dir = 0
                _flick_peak = 0.0

    elif _flick_state == _FLICK_LOCKED:
        # Only an opposite-direction flick can override the lock here.
        # (FIST clearing is handled separately via reset_flick_state().)
        if sign == -_flick_dir and mag >= FLICK_GOING_THRESHOLD:
            _flick_state = _FLICK_GOING
            _flick_dir = sign
            _flick_peak = mag
        # otherwise: stay locked, regardless of deceleration etc.

    return _flick_dir if _flick_state == _FLICK_LOCKED else 0


def reset_flick_state():
    """Clear any flick lock/progress (e.g. on FIST or round reset)."""
    global _flick_state, _flick_dir, _flick_peak, _last_avg_sx, _last_time
    _flick_state = _FLICK_NONE
    _flick_dir = 0
    _flick_peak = 0.0
    _sx_history.clear()
    _last_avg_sx = 0.0
    _last_time = time()


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
      - In "acceleration" mode, left/right intent comes from flick
        detection on a 5-sample moving average of hand speed: an
        outgoing acceleration >= 0.8*MAX_HAND_ACC followed by a return
        acceleration <= 0.9x the outgoing peak locks that direction.
        The lock holds until FIST or an opposite-direction flick.
    """
    global _last_avg_sx, _last_time

    state = control["state"]
    dx_cm, dy_cm = control["relative_cm"]

    x_dir, y_dir = _direction_from_position(dx_cm, dy_cm)

    # Arrow-style directions from hand position.
    right = x_dir == 1
    left = x_dir == -1
    down = y_dir == 1
    up = y_dir == -1

    flick_dir = None  # only set in acceleration mode

    if state == HandGesture.FIST:
        up = down = left = right = False
        reset_flick_state()
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
    if "speed" in control:
        sx, _sy = control["speed"]
        now = time()
        dt = now - _last_time

        if HAND_INPUT_METHOD == "speed":
            vx = max(-1.0, min(1.0, sx / MAX_HAND_SPEED))
        elif HAND_INPUT_METHOD == "acceleration":
            avg_sx = _moving_average_sx(sx)

            if dt > 0:
                ax = (_last_avg_sx- avg_sx) / dt
            else:
                ax = 0.0
            ax_norm = max(-1.0, min(1.0, ax / MAX_HAND_ACC))

            if state != HandGesture.FIST:
                flick_dir = _update_flick(ax_norm)
            else:
                flick_dir = 0

            vx = float(flick_dir) if flick_dir else 0.0

            _last_avg_sx = avg_sx
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

    # If we're in acceleration/flick mode, the flick lock also drives
    # left/right flags (so callers checking `left`/`right` stay consistent
    # with `vx`), unless FIST has already cleared everything.
    if flick_dir is not None and state != HandGesture.FIST:
        _flick_state = _FLICK_NONE
        if flick_dir == 1:
            right, left = True, False
        elif flick_dir == -1:
            left, right = True, False
        # flick_dir == 0 -> leave left/right as derived from position/keys

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