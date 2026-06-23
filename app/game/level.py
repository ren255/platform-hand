# app/game/level.py
"""level.py

Stage definitions and LevelManager: owns stage transitions and
collision-outcome judgement (death / goal). Knows nothing about Player
internals — only consumes a pygame.Rect for checks.
"""

import pygame

from app.game.physics import _check_spike_collision
from app.game.color import RED, GREEN, GRAY
from app.game.stages import Stage,STAGES


class LevelManager:
    def __init__(self, stages: list[Stage] = STAGES):
        self.stages = stages
        self.index = 0
    @property
    def stage(self) -> Stage:
        return self.stages[self.index]

    def current_blocks(self):
        """Blocks Player should collide with (ground/platforms only)."""
        return self.stage.blocks

    def start_pos(self):
        return self.stage.start_pos

    def check(self, rect: pygame.Rect) -> str:
        """Check rect against spikes/goal for this stage.

        Returns one of: "dead", "goal", "none".
        """
        if _check_spike_collision(rect, self.stage.spikes):
            return "dead"
        if rect.colliderect(self.stage.goal_line):
            return "goal"
        return "none"

    def advance(self):
        """Move to the next stage if one exists. Returns True if advanced."""
        if self.index + 1 < len(self.stages):
            self.index += 1
            return True
        return False

    def draw(self, screen):
        for block in self.stage.blocks:
            pygame.draw.rect(screen, GRAY, block)
        for spike in self.stage.spikes:
            pygame.draw.rect(screen, RED, spike)
        pygame.draw.rect(screen, GREEN, self.stage.goal_line)