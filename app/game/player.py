import pygame
from app.config import WINDOW_W, WINDOW_H
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
    
    def update(self,pos):
        self.rect.x,self.rect.y = pos[0],pos[1]

    def draw(self):
        pygame.draw.rect(self.screen, (240, 240, 240), self.rect)
