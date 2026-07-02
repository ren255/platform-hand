# app/game/game.py
"""game/game.py

Pygame game window only. Combines camera/hand control (received via a
queue) with the window's own keyboard input through compute_input(),
applies gravity, and moves a square with collisions against the
current stage's blocks. Stage progression, death, and goal handling
are delegated to LevelManager.
"""

import pygame

from app.game.input import compute_input
from app.hand.gesture import HandGesture
from app.game.player import Player
from app.game.level import LevelManager
import time

from app.config import WINDOW_W, WINDOW_H


# Fallback control used when no hand data has arrived yet from the camera
# process (e.g. at startup, or no hand currently detected).
IDLE_CONTROL = {"state": HandGesture.NONE, "relative_cm": (0.0, 0.0)}


def _keys_from_pygame(pressed):
    """Build a plain dict from pygame's key state for compute_input()."""
    return {
        "up": pressed[pygame.K_UP] or pressed[pygame.K_w],
        "down": pressed[pygame.K_DOWN] or pressed[pygame.K_s],
        "left": pressed[pygame.K_LEFT] or pressed[pygame.K_a],
        "right": pressed[pygame.K_RIGHT] or pressed[pygame.K_d],
    }

def _format_time(ms):
    "ms -> mm:ss:ms"
    total_seconds = ms / 1000
    minutes = int(total_seconds //60)
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:06.3f}"


def run_game_window(control_queue):
    """Main loop for the game window. Blocks until the window is closed."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("game_test - game window")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None,36)
    

    level = LevelManager()
    player = Player(screen)
    player.rect.topleft = level.start_pos()

    last_control = IDLE_CONTROL
    timer_running = True
    elapsed_ms = 0
    start_time = time.time()

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

        player.update(input_dict, level.current_blocks())

        # --- Stage outcome judgement (game.py is the sole decision-maker) ---
        outcome = level.check(player.rect)
        if outcome == "dead":
            player.rect.topleft = level.start_pos()
            player.vel_y = 0
        elif outcome == "goal":
            if level.advance():
                player.rect.topleft = level.start_pos()
                player.vel_y = 0
                if level.is_clear_stage():
                    timer_running = False
            else:
                timer_running = False
                running = False  # no more stages; could show a clear screen instead

        # --- Draw ---
        screen.fill((20, 20, 20))
        level.draw(screen)
        player.draw()
        
        elapsed_ms = (time.time() - start_time) * 1000 if timer_running else elapsed_ms
        timer_text = font.render(_format_time(elapsed_ms),True,(255,255,255))
        screen.blit(timer_text,(10,10))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()