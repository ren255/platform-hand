import cv2
import pygame

from app.hand.camera import HAND_CONNECTIONS


def frame_to_surface(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = cv2.flip(rgb, 1)
    return pygame.surfarray.make_surface(rgb.swapaxes(0, 1))


def draw_landmarks(screen, result, width, height):
    if not result.hand_landmarks:
        return

    for hand in result.hand_landmarks:
        points = [
            (int((1 - lm.x) * width), int(lm.y * height)) for lm in hand
        ]

        for start, end in HAND_CONNECTIONS:
            pygame.draw.line(screen, (0, 255, 0), points[start], points[end], 2)

        for x, y in points:
            pygame.draw.circle(screen, (255, 0, 0), (x, y), 5)
