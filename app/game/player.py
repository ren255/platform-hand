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
from app.game.sprite import Direction, load_player_animations
from app.hand.gesture import HandGesture

MAX_DELTA_S = 1.0 / 20.0  # 20fps相当を下限

_ANIMATIONS = None  # 遅延ロード用


def _get_animations():
    global _ANIMATIONS
    if _ANIMATIONS is None:
        _ANIMATIONS = load_player_animations()
    return _ANIMATIONS


class Player:
    def __init__(self, screen):
        self.screen = screen
        self.animations = _get_animations()

        self.facing = Direction.RIGHT

        frame_w, frame_h = self.animations[self.facing].stop_frame.get_size()
        self.rect = pygame.Rect(
            WINDOW_W // 2 - frame_w // 2,
            WINDOW_H // 2 - frame_h // 2,
            frame_w,
            frame_h,
        )

        self.on_ground = False
        self.vel_y = 0.0
        self.last_time = time.time()

    def _update_facing_and_animation(self, vx, delta_s, input_dict):
        if vx > 0:
            self.facing = Direction.RIGHT
        elif vx < 0:
            self.facing = Direction.LEFT

        if input_dict["state"] == HandGesture.FIST:
            self.facing = Direction.FRONT

        for direction, anim in self.animations.items():
            if direction == self.facing and (
                input_dict["state"] == HandGesture.FIST or vx != 0
            ):
                anim.play()
            else:
                anim.stop()
            anim.update(delta_s)

    def update(self, input_dict, BLOCKS):
        now = time.time()
        delta_s = min(now - self.last_time, MAX_DELTA_S)
        self.last_time = now

        vx = input_dict["vx"]

        self.rect.x += int(vx * MOVE_SPEED * delta_s)
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

        self._update_facing_and_animation(vx, delta_s, input_dict)

    def draw(self):
        frame = self.animations[self.facing].current_frame()
        self.screen.blit(frame, self.rect.topleft)
