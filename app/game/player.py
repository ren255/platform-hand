import pygame
import time

from app.config import (
    WINDOW_W,
    WINDOW_H,
    MOVE_SPEED,
    JUMP_SPEED,
    GRAVITY,
    MAX_FALL_SPEED,
)
from app.game.physics import (
    _resolve_horizontal_collisions,
    _resolve_vertical_collisions,
)

MAX_DELTA_S = 1.0 / 20.0  # 20fps相当を下限


class Player:
    def __init__(self, screen):
        self.screen = screen
        self.size = 40
        self.rect = pygame.Rect(
            WINDOW_W // 2 - self.size // 2,
            WINDOW_H // 2 - self.size // 2,
            self.size,
            self.size,
        )
        self.on_ground = False
        self.vel_y = 0.0  # px/秒
        self.last_time = time.time()
        self.fps_list = []

    def update(self, input_dict, BLOCKS):
        now = time.time()
        delta_s = min(now - self.last_time, MAX_DELTA_S)
        self.last_time = now
        fps = 1 / delta_s if delta_s > 0 else 60
        self.fps_list.append(fps)
        if len(self.fps_list) > 10:
            self.fps_list.pop(0)
        print(f"FPS: {sum(self.fps_list) / len(self.fps_list):.2f}")

        self.rect.x += int(input_dict["vx"] * MOVE_SPEED * delta_s)
        self.rect.x = max(0, min(WINDOW_W - self.rect.width, self.rect.x))
        self.rect = _resolve_horizontal_collisions(
            self.rect, input_dict["left"], input_dict["right"], BLOCKS
        )

        if input_dict["want_jump"] and self.on_ground:
            self.vel_y = JUMP_SPEED

        self.vel_y = min(self.vel_y + GRAVITY * delta_s, MAX_FALL_SPEED)

        dy = int(self.vel_y * delta_s)
        self.rect.y += dy

        self.rect, self.vel_y, self.on_ground = _resolve_vertical_collisions(
            self.rect, self.vel_y, dy, BLOCKS
        )

        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0

        if self.rect.bottom > WINDOW_H:
            self.rect.bottom = WINDOW_H
            self.vel_y = 0
            self.on_ground = True

    def draw(self):
        pygame.draw.rect(self.screen, (240, 240, 240), self.rect)