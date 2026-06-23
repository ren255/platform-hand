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
from app.game.player import Player

from app.config import MOVE_SPEED, GRAVITY, JUMP_SPEED, MAX_FALL_SPEED,WINDOW_W, WINDOW_H



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




def run_game_window(control_queue):
    """Main loop for the game window. Blocks until the window is closed."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("game_test - game window")
    clock = pygame.time.Clock()

    player = Player(screen)

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

        
        player.update(input_dict,BLOCKS)       
    

        # --- Draw ---
        screen.fill((20, 20, 20))
        for block in BLOCKS:
            pygame.draw.rect(screen, (90, 90, 90), block)
        player.draw()
        pygame.display.flip()
        clock.tick(60)
        

    pygame.quit()