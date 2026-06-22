# app/game/game.py
"""game/game.py

Pygame game window only. Combines camera/hand control (received via a
queue) with the window's own keyboard input through compute_input(),
applies gravity, and moves a square with collisions against fixed
blocks.

This module has no knowledge of how the camera process is started; it
only consumes a `control_queue` that's handed to it.
"""

import pygame

from app.game.input import compute_input
from app.hand.gesture import HandGesture

from app.config import MOVE_SPEED, GRAVITY, JUMP_SPEED, MAX_FALL_SPEED


WINDOW_W, WINDOW_H = 640, 480
SQUARE_SIZE = 40

# Fallback control used when no hand data has arrived yet from the camera
# process (e.g. at startup, or no hand currently detected).
IDLE_CONTROL = {"state": HandGesture.NONE, "relative_cm": (0.0, 0.0)}

# Fixed blocks (platforms/ground), as pygame.Rect(x, y, w, h).
BLOCKS = [
    pygame.Rect(0, WINDOW_H - 30, WINDOW_W, 30),     # ground
    pygame.Rect(150, 400, 120, 20),                   # platform 1
    pygame.Rect(350, 370, 250, 20),                   # platform 2
    pygame.Rect(50, 300, 180, 20),                    # platform 3
]


def _keys_from_pygame(pressed):
    """Build a plain dict from pygame's key state for compute_input()."""
    return {
        "up": pressed[pygame.K_UP] or pressed[pygame.K_w],
        "down": pressed[pygame.K_DOWN] or pressed[pygame.K_s],
        "left": pressed[pygame.K_LEFT] or pressed[pygame.K_a],
        "right": pressed[pygame.K_RIGHT] or pressed[pygame.K_d],
    }

#
def _resolve_vertical_collisions(rect, vel_y, blocks):
    """Resolve vertical collisions between `rect` and fixed `blocks`.

    Returns (rect, vel_y, on_ground).
    """

    on_ground = False
    for block in blocks:
        if rect.colliderect(block):
            if vel_y > 0 and rect.bottom - vel_y <= block.top + 1:
                rect.bottom = block.top
                vel_y = 0
                on_ground = True
            elif vel_y < 0 and rect.top - vel_y >= block.bottom - 1:
                rect.top = block.bottom
                vel_y = 0
    return rect, vel_y, on_ground


def _resolve_horizontal_collisions(rect, moving_left, moving_right, blocks):
    """Simple push-out against blocks for horizontal movement."""

    for block in blocks:
        if rect.colliderect(block):
            if moving_right and not moving_left:
                rect.right = block.left
            elif moving_left and not moving_right:
                rect.left = block.right
    return rect


def run_game_window(control_queue):
    """Main loop for the game window. Blocks until the window is closed."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("game_test - game window")
    clock = pygame.time.Clock()

    rect = pygame.Rect(
        WINDOW_W // 2 - SQUARE_SIZE // 2,
        WINDOW_H // 2 - SQUARE_SIZE // 2,
        SQUARE_SIZE,
        SQUARE_SIZE,
    )
    vel_y = 0.0
    on_ground = False

    last_control = IDLE_CONTROL

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Pull the latest hand control if available; otherwise keep using
        # the last known one (camera process pushes at its own pace).
        if control_queue is not None:
            try:
                last_control = control_queue.get_nowait()
            except Exception:
                pass

        keys = _keys_from_pygame(pygame.key.get_pressed())
        input_dict = compute_input(last_control, keys=keys)

        # --- Horizontal movement (driven entirely by input.py's vx) ---
        rect.x += int(input_dict["vx"] * MOVE_SPEED)
        rect.x = max(0, min(WINDOW_W - rect.width, rect.x))
        rect = _resolve_horizontal_collisions(
            rect, input_dict["left"], input_dict["right"], BLOCKS
        )

        # --- Jump (physics decides if it's allowed) ---
        if input_dict["want_jump"] and on_ground:
            vel_y = JUMP_SPEED

        # --- Gravity ---
        vel_y = min(vel_y + GRAVITY, MAX_FALL_SPEED)
        rect.y += int(vel_y)

        rect, vel_y, on_ground = _resolve_vertical_collisions(rect, vel_y, BLOCKS)

        # Keep within the window vertically as a safety net.
        if rect.top < 0:
            rect.top = 0
            vel_y = 0
        if rect.bottom > WINDOW_H:
            rect.bottom = WINDOW_H
            vel_y = 0
            on_ground = True

        # --- Draw ---
        screen.fill((20, 20, 20))
        for block in BLOCKS:
            pygame.draw.rect(screen, (90, 90, 90), block)
        pygame.draw.rect(screen, (240, 240, 240), rect)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()