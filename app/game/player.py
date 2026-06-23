import pygame
from app.config import WINDOW_W, WINDOW_H,MOVE_SPEED,JUMP_SPEED,GRAVITY,MAX_FALL_SPEED
from app.game.physics import _resolve_horizontal_collisions,_resolve_vertical_collisions
class Player:
    def __init__(self,screen):
        self.screen = screen
        self.size = 40
        self.rect = pygame.Rect(
            WINDOW_W // 2 - self.size // 2,
            WINDOW_H // 2 - self.size // 2,
            self.size,
            self.size,
        )
        self.on_ground = False
        self.vel_y = 0
    
    def update(self,input_dict,BLOCKS,):
        # --- Horizontal movement (driven entirely by input.py's vx) ---
        self.rect.x += int(input_dict["vx"] * MOVE_SPEED)
        self.rect.x = max(0, min(WINDOW_W - self.rect.width, self.rect.x))
        self.rect = _resolve_horizontal_collisions(
            self.rect, input_dict["left"], input_dict["right"], BLOCKS
        )

        # --- Jump (physics decides if it's allowed) ---
        if input_dict["want_jump"] and self.on_ground:
            self.vel_y = JUMP_SPEED

        # --- Gravity ---
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        self.rect.y += int(self.vel_y)

        self.rect, self.vel_y, self.on_ground = _resolve_vertical_collisions(self.rect, self.vel_y, BLOCKS)
        
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0
            
        if self.rect.bottom > WINDOW_H:
            self.rect.bottom = WINDOW_H
            self.vel_y = 0
            self.on_ground = True

    def draw(self):
        pygame.draw.rect(self.screen, (240, 240, 240), self.rect)
