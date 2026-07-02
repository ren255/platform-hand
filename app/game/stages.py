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
        start_pos=(50, 600),
        goal_line=pygame.Rect(1470, 0, 30, 800),
        blocks=[
            pygame.Rect(0, 700, 800, 100),
            pygame.Rect(400, 600, 100, 100),
            pygame.Rect(1000, 700, 500, 100),
        ],
        spikes=[
            pygame.Rect(800, 750, 200, 50),
        ],
    ),

    # Stage 1: staircase platforms
    Stage(
        start_pos=(50, 600),
        goal_line=pygame.Rect(1470, 0, 30, 800),
        blocks=[
            pygame.Rect(0, 650, 200, 150),
            pygame.Rect(200, 650, 150, 20),
            pygame.Rect(450, 530, 150, 20),
            pygame.Rect(700, 410, 150, 20),
            pygame.Rect(1100, 650,300, 20),
        ],
        spikes=[
            pygame.Rect(200, 750, 1300, 50),
        ],
    ),

    # Stage 2: spike gauntlet on the ground
    Stage(
        start_pos=(50, 600),
        goal_line=pygame.Rect(1470, 0, 30, 800),
        blocks=[
            pygame.Rect(0, 770, 1500, 30),
            
            pygame.Rect(200, 0, 100, 700),
            pygame.Rect(750, 100, 100, 670),
            pygame.Rect(1300, 0, 100, 700),
            
            pygame.Rect(650, 650, 100, 50),
            pygame.Rect(300, 500, 250, 50),
            pygame.Rect(300, 350, 100, 50),
            pygame.Rect(500, 200, 150, 50),
            pygame.Rect(850, 100, 150, 10),
            
        ],
        spikes=[
            pygame.Rect(850, 200, 200, 30),
            pygame.Rect(950, 600, 350, 30),
        ],
    ),

    # Stage 3: floating islands, no continuous ground
    Stage(
        start_pos=(50, 300),
        goal_line=pygame.Rect(1470, 0, 30, 800),
        blocks=[
            pygame.Rect(0, 350, 200, 10),
            pygame.Rect(300, 350, 150, 10),
            pygame.Rect(500, 350, 150, 10),
            
            pygame.Rect(680, 550, 120, 10),
            pygame.Rect(850, 550, 120, 10),
            
            pygame.Rect(1050, 450, 100, 10),
            pygame.Rect(1200, 450, 100, 10),
            
            pygame.Rect(1350, 600, 120, 10),
            
        ],
        spikes=[
            pygame.Rect(0, 650, 1500, 150),
            pygame.Rect(450, 310, 50, 50),
            pygame.Rect(800, 510, 50, 50),
            pygame.Rect(1150, 410, 50, 50),
            pygame.Rect(650, 0, 50, 270),
            pygame.Rect(1350, 0, 50, 370),
        ],
    ),
    # Stage 4: floating islands, no continuous ground
    Stage(
        start_pos=(50, 250),
        goal_line=pygame.Rect(1470, 0, 30, 800),
        blocks=[
            pygame.Rect(0, 600, 1500, 200),
            
            pygame.Rect(50, 300, 200, 50),
            pygame.Rect(50, 350, 50, 150),
            pygame.Rect(50, 500, 200, 50),
            
            pygame.Rect(300, 300, 50, 200),
            pygame.Rect(300, 500, 200, 50),
            
            pygame.Rect(550, 300, 200, 50),
            pygame.Rect(550, 350, 50, 200),
            pygame.Rect(600, 400, 100, 50),
            pygame.Rect(600, 500, 150, 50),
            
            
            pygame.Rect(900, 300, 50, 50),
            pygame.Rect(950,350, 50, 50),
            pygame.Rect(850, 350, 50, 50),
            pygame.Rect(1000,400, 50, 150),
            pygame.Rect(800, 400, 50, 150),
            pygame.Rect(850, 450, 150, 50),
            
            pygame.Rect(1100, 300, 50, 250),
            pygame.Rect(1150, 300, 150, 50),
            pygame.Rect(1150, 400, 150, 50),
            pygame.Rect(1300, 350, 50, 50),
            pygame.Rect(1200, 450, 50, 50),
            pygame.Rect(1250, 500, 100, 50),
            
            pygame.Rect(1400, 300, 50, 150),
            pygame.Rect(1400, 500, 50, 50),
            
        ],
        spikes=[],
    ),
]

