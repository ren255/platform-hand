from dataclasses import dataclass, field
import pygame


@dataclass
class Stage:
    start_pos: tuple[int, int]
    goal_line: pygame.Rect
    blocks: list[pygame.Rect] = field(default_factory=list)
    spikes: list[pygame.Rect] = field(default_factory=list)


STAGES: list[Stage] = [
    # Stage 0: simple ground run with a gap
    Stage(
        start_pos=(50, 700),
        goal_line=pygame.Rect(1450, 0, 10, 800),
        blocks=[
            pygame.Rect(0, 770, 600, 30),
            pygame.Rect(700, 770, 800, 30),
        ],
        spikes=[
            pygame.Rect(600, 750, 100, 20),
        ],
    ),

    # Stage 1: staircase platforms
    Stage(
        start_pos=(50, 700),
        goal_line=pygame.Rect(1450, 0, 10, 800),
        blocks=[
            pygame.Rect(0, 770, 1500, 30),
            pygame.Rect(200, 650, 150, 20),
            pygame.Rect(450, 530, 150, 20),
            pygame.Rect(700, 410, 150, 20),
            pygame.Rect(950, 290, 150, 20),
            pygame.Rect(1200, 170, 150, 20),
        ],
        spikes=[],
    ),

    # Stage 2: spike gauntlet on the ground
    Stage(
        start_pos=(50, 700),
        goal_line=pygame.Rect(1450, 0, 10, 800),
        blocks=[
            pygame.Rect(0, 770, 1500, 30),
            pygame.Rect(500, 600, 200, 20),
            pygame.Rect(900, 450, 200, 20),
        ],
        spikes=[
            pygame.Rect(300, 750, 40, 20),
            pygame.Rect(500, 750, 40, 20),
            pygame.Rect(700, 750, 40, 20),
            pygame.Rect(1100, 750, 40, 20),
            pygame.Rect(1200, 750, 40, 20),
        ],
    ),

    # Stage 3: floating islands, no continuous ground
    Stage(
        start_pos=(50, 300),
        goal_line=pygame.Rect(1450, 0, 10, 800),
        blocks=[
            pygame.Rect(0, 350, 200, 20),
            pygame.Rect(300, 450, 150, 20),
            pygame.Rect(550, 350, 150, 20),
            pygame.Rect(800, 250, 150, 20),
            pygame.Rect(1050, 400, 150, 20),
            pygame.Rect(1300, 300, 200, 20),
        ],
        spikes=[
            pygame.Rect(250, 770, 1000, 30),
        ],
    ),
]

