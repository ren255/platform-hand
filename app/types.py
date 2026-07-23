"""Shared dataclasses for the hand-control -> game-input pipeline.

These types are intentionally simple (and picklable) so they can safely be
passed through multiprocessing queues between the camera process and the game
process.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

from app.hand.gesture import HandGesture


@dataclass
class HandControl:
    """Raw control output produced by the hand controller."""

    state: HandGesture
    relative_cm: Tuple[float, float]
    origin_px: Tuple[int, int]
    speed: Tuple[float, float]


@dataclass
class InputState:
    """Unified input state consumed by the player and UI."""

    up: bool
    down: bool
    left: bool
    right: bool
    vx: float
    want_jump: bool
    state: HandGesture
    relative_cm: Tuple[float, float]
    flick_event: Optional[str] = None  # None / "left" / "right"
    flick_locked_dir: int = 0  # -1 / 0 / +1
