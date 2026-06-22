# game/move_test.py
"""game/move_test.py

Launch the hand camera window (separate process, produces hand-based control
via the queue) and a pygame "game window" in the main process. Both the
camera/hand input AND the game window's own keyboard input are fed into
compute_input(), which combines them into unified up/down/left/right flags.

A square is moved on screen:
  - left/right: horizontal movement
  - up: jump (only works when standing on ground/a block)
  - gravity pulls the square down continuously
  - a few fixed blocks act as platforms/ground to land on

Run with: python -m game.move_test
"""

import sys
from multiprocessing import Event, Process, Queue

import pygame

from app.game.input import compute_input
from app.hand.camera_window import run_camera_window
from app.hand.gesture import HandGesture

from app.config import (MOVE_SPEED,GRAVITY,JUMP_SPEED,MAX_FALL_SPEED,HAND_INPUT_METHOD,MAX_HAND_SPEED)
WINDOW_W, WINDOW_H = 640, 480
SQUARE_SIZE = 40

# Fallback control used when no hand data has arrived yet from the camera
# process (e.g. at startup, or no hand currently detected).
_IDLE_CONTROL = {"state": HandGesture.NONE, "relative_cm": (0.0, 0.0)}

# Fixed blocks (platforms/ground), as pygame.Rect(x, y, w, h).
BLOCKS = [
    pygame.Rect(0, WINDOW_H - 30, WINDOW_W, 30),     # ground
    pygame.Rect(150, 400, 120, 20),                   # platform 1
    pygame.Rect(350, 370, 250, 20),                   # platform 2
    pygame.Rect(50, 300, 180, 20),                    # platform 3
]


def _keys_from_pygame(pressed):
    """Build the `keys` dict compute_input expects from pygame's key state."""
    return {
        "up": pressed[pygame.K_UP] or pressed[pygame.K_w],
        "down": pressed[pygame.K_DOWN] or pressed[pygame.K_s],
        "left": pressed[pygame.K_LEFT] or pressed[pygame.K_a],
        "right": pressed[pygame.K_RIGHT] or pressed[pygame.K_d],
    }


def _resolve_collisions(rect, vel_y, blocks):
    """Resolve vertical collisions between `rect` and fixed `blocks`.

    Horizontal movement is applied separately/before this, so this only
    handles falling onto / hitting blocks vertically. Returns the
    (possibly adjusted) rect, the (possibly zeroed) vel_y, and whether the
    square is currently standing on a block (on_ground).
    """
    on_ground = False
    for block in blocks:
        if rect.colliderect(block):
            if vel_y > 0 and rect.bottom - vel_y <= block.top + 1:
                # Falling onto the top of the block.
                rect.bottom = block.top
                vel_y = 0
                on_ground = True
            elif vel_y < 0 and rect.top - vel_y >= block.bottom - 1:
                # Hitting the underside of the block while jumping.
                rect.top = block.bottom
                vel_y = 0
    return rect, vel_y, on_ground


def run_game_window(control_queue):
    """Pygame window: combines camera/hand control + own keyboard input via
    compute_input(), applies gravity, and moves a square with collisions
    against fixed blocks."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("move_test - game window")
    clock = pygame.time.Clock()

    rect = pygame.Rect(
        WINDOW_W // 2 - SQUARE_SIZE // 2,
        WINDOW_H // 2 - SQUARE_SIZE // 2,
        SQUARE_SIZE,
        SQUARE_SIZE,
    )
    vel_y = 0.0
    on_ground = False

    last_control = _IDLE_CONTROL

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Pull the latest hand control if available; otherwise keep using
        # the last known one (camera process pushes at its own pace).
        try:
            last_control = control_queue.get_nowait()
        except Exception:
            pass

        keys = _keys_from_pygame(pygame.key.get_pressed())
        input_dict = compute_input(last_control, keys=keys)

        if HAND_INPUT_METHOD == "distance":
            # --- Horizontal movement ---
            if input_dict["left"]:
                rect.x -= MOVE_SPEED
            if input_dict["right"]:
                rect.x += MOVE_SPEED
            rect.x = max(0, min(WINDOW_W - rect.width, rect.x))

            # --- Gravity / jump ---
            if input_dict["up"] and on_ground:
                vel_y = JUMP_SPEED
        elif HAND_INPUT_METHOD == "speed":
            # --- Horizontal movement ---
            rect.x += (input_dict["speed"][0] / MAX_HAND_SPEED) * MOVE_SPEED
            rect.x = max(0, min(WINDOW_W - rect.width, rect.x))

            if input_dict["speed"][1] > MAX_HAND_SPEED / 2: # 上向きで最大マップ手速度の半分の時ジャンプ
                vel_y = JUMP_SPEED
        
        # Resolve horizontal collisions (simple push-out against blocks).
        for block in BLOCKS:
            if rect.colliderect(block):
                if input_dict["right"] and not input_dict["left"]:
                    rect.right = block.left
                elif input_dict["left"] and not input_dict["right"]:
                    rect.left = block.right

        vel_y = min(vel_y + GRAVITY, MAX_FALL_SPEED)
        rect.y += int(vel_y)

        rect, vel_y, on_ground = _resolve_collisions(rect, vel_y, BLOCKS)

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


def main():
    """Launch camera window (separate process) + game window (main process)."""
    control_queue = Queue(maxsize=1)
    stop_event = Event()

    camera_process = Process(
        target=run_camera_window,
        args=(control_queue, stop_event),
        name="CameraWindow",
    )
    camera_process.start()

    try:
        run_game_window(control_queue)
    finally:
        stop_event.set()
        camera_process.join(timeout=3)
        if camera_process.is_alive():
            camera_process.terminate()
            camera_process.join(timeout=2)


if __name__ == "__main__":
    sys.exit(main())