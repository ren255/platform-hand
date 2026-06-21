import sys
import time

import cv2
import pygame

from app.hand.camera import Camera, HandTracker
from app.hand.renderer import draw_landmarks, frame_to_surface


def main():
    pygame.init()

    camera = Camera()
    width, height = camera.width, camera.height
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    tracker = HandTracker()
    start_time = time.time()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

        ok, frame = camera.read()
        if not ok:
            continue

        timestamp_ms = int((time.time() - start_time) * 1000)
        result = tracker.process(frame, timestamp_ms)
        surface = frame_to_surface(frame)
        screen.blit(surface, (0, 0))
        draw_landmarks(screen, result, width, height)
        pygame.display.flip()

        clock.tick(30)

    tracker.close()
    camera.release()
    pygame.quit()


if __name__ == "__main__":
    main()
