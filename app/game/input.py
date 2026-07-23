# app/game/input.py
"""Pure input-combination logic: camera/hand control + keyboard flags
-> unified directional intent + normalized speed vector.

No pygame dependency here. The caller (game.py) is responsible for
converting raw pygame key state into a plain dict before calling
update().
"""

import time
import math

from app.config import (
    WASD,
    DEADZONE_CM,
    HAND_INPUT_METHOD,
    MAX_HAND_SPEED,
    WINDOW_W,
    WINDOW_H,
    HAND_EMA_ALPHA,
    FLICK_MIN_SPEED,
    FLICK_MIN_ACCELERATION,
    FLICK_MAX_ACCELERATION,
)
from app.hand.gesture import HandGesture
from app.types import HandControl, InputState


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


def _merge_keys(keys):
    if not keys:
        return False, False, False, False

    up = bool(keys.get("up") or keys.get("w"))
    down = bool(keys.get("down") or keys.get("s"))
    left = bool(keys.get("left") or keys.get("a"))
    right = bool(keys.get("right") or keys.get("d"))
    return up, down, left, right


class HandInputController:
    """Stateful hand-input processor.

    Responsibilities:
    - Smooth speed with an EMA (used for smoothing only, not as a
      second source of truth).
    - Detect flicks from speed/acceleration magnitude.
    - Merge keyboard input and produce a unified InputState.

    The acceleration source of truth remains ``control.speed`` when
    ``HAND_INPUT_METHOD == "acceleration"``; the EMA is smoothing only.
    """

    def __init__(self):
        # EMA smoothing (not the acceleration source of truth)
        self._ema_speed = (0.0, 0.0)

        # Flick direction lock (0 = none, 1 = right, -1 = left)
        self._locked_dir = 0

        # Time-based dt for cm/s and cm/s^2 calculations
        self._last_time = None

        # Exposed for optional external logging
        self._last_speed_mag = 0.0
        self._last_accel_mag = 0.0

    def reset(self):
        """Clear all state; called on FIST or round reset."""
        self.__init__()

    def update(self, control: HandControl, keys=None) -> InputState:
        """Convert hand-control + (optional) keyboard input into unified
        directional input flags AND a normalized speed vector.

        Returns an InputState with up/down/left/right flags, vx (normalized
        speed, -1..1), want_jump, state, relative_cm, flick_event, and
        flick_locked_dir.
        """
        state = control.state
        dx_cm, dy_cm = control.relative_cm

        # 1. Ingest the new sample; update EMA and compute speed/acceleration.
        is_new = self._ingest_sample(control.speed)

        # 2. Update flick lock on genuinely new samples.
        if is_new:
            self._update_flick_lock(
                self._last_speed_mag, self._last_accel_mag, self._ema_speed[0]
            )

        # 3. Derive directional intent from hand position.
        x_dir, y_dir = _direction_from_position(dx_cm, dy_cm)

        right = x_dir == 1
        left = x_dir == -1
        down = y_dir == 1
        up = y_dir == -1

        if state == HandGesture.FIST:
            up = down = left = right = False
            self.reset()
        elif state == HandGesture.OPEN:
            up = True
            down = False

        # 4. Merge keyboard input.
        key_up, key_down, key_left, key_right = _merge_keys(keys)
        up = up or key_up
        down = down or key_down
        left = left or key_left
        right = right or key_right

        # 5. Normalized horizontal speed intent.
        flick_event = None
        if self._locked_dir != 0:
            vx = float(self._locked_dir)
            flick_event = "right" if self._locked_dir == 1 else "left"
        elif HAND_INPUT_METHOD == "speed":
            sx, _sy = control.speed
            vx = max(-1.0, min(1.0, sx / MAX_HAND_SPEED))
        elif HAND_INPUT_METHOD == "acceleration":
            # Acceleration mode uses control.speed as the primary signal.
            # The flick state machine already determined the direction.
            vx = float(self._locked_dir)
        else:
            # "distance" mode: derive from flags.
            vx = 0.0
            if right and not left:
                vx = 1.0
            elif left and not right:
                vx = -1.0

        # Keep left/right flags consistent with the flick lock.
        if self._locked_dir == 1:
            right, left = True, False
        elif self._locked_dir == -1:
            left, right = True, False

        # Keyboard overrides/adds to vx as full-speed intent.
        if key_right and not key_left:
            vx = 1.0
        elif key_left and not key_right:
            vx = -1.0

        return InputState(
            up=up,
            down=down,
            left=left,
            right=right,
            vx=vx,
            want_jump=up,
            state=state,
            relative_cm=(dx_cm, dy_cm),
            flick_event=flick_event,
            flick_locked_dir=self._locked_dir,
        )

    def _ingest_sample(self, raw_speed) -> bool:
        """Ingest a raw speed sample.

        Returns True if the sample is genuinely new. Duplicate samples are
        no longer filtered; every call is treated as a new sample.
        """
        sx, sy = raw_speed

        now = time.perf_counter()
        if self._last_time is None:
            self._last_time = now
            self._ema_speed = (float(sx), float(sy))
            self._last_speed_mag = 0.0
            self._last_accel_mag = 0.0
            return False  # first frame has no dt; skip state machine

        dt = now - self._last_time
        self._last_time = now
        if dt <= 0.0:
            dt = 1e-6

        prev_ema_sx, prev_ema_sy = self._ema_speed

        # Update EMA for both x and y speed components.
        ema_sx = HAND_EMA_ALPHA * sx + (1.0 - HAND_EMA_ALPHA) * prev_ema_sx
        ema_sy = HAND_EMA_ALPHA * sy + (1.0 - HAND_EMA_ALPHA) * prev_ema_sy
        self._ema_speed = (ema_sx, ema_sy)

        # Speed magnitude in cm/s (assumes control.speed is already cm/s).
        speed_mag = math.hypot(ema_sx, ema_sy)
        self._last_speed_mag = speed_mag

        # Acceleration magnitude in cm/s^2 from smoothed speed deltas.
        dvx = ema_sx - prev_ema_sx
        dvy = ema_sy - prev_ema_sy
        accel_mag = math.hypot(dvx, dvy) / dt

        # Reject anomalous spikes.
        if accel_mag > FLICK_MAX_ACCELERATION:
            accel_mag = 0.0
        self._last_accel_mag = accel_mag

        return True

    def _update_flick_lock(self, speed_mag, accel_mag, ema_vel_x):
        """Update flick lock direction from speed/acceleration magnitude."""

        def _sign(value):
            if value > 0:
                return 1
            if value < 0:
                return -1
            return 0

        if (
            FLICK_MIN_ACCELERATION <= accel_mag <= FLICK_MAX_ACCELERATION
            and speed_mag >= FLICK_MIN_SPEED
        ):
            self._locked_dir = _sign(ema_vel_x)
