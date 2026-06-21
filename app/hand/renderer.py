import cv2
import pygame

from app.hand.camera import HAND_CONNECTIONS


def frame_to_surface(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = cv2.flip(rgb, 1)
    return pygame.surfarray.make_surface(rgb.swapaxes(0, 1))


def _draw_single_hand(screen, hand, width, height, line_color, joint_color):
    points = [
        (int((1 - lm.x) * width), int(lm.y * height)) for lm in hand
    ]

    for start, end in HAND_CONNECTIONS:
        pygame.draw.line(screen, line_color, points[start], points[end], 2)

    for x, y in points:
        pygame.draw.circle(screen, joint_color, (x, y), 3)


def _draw_average_position(screen, avg_pos, width, height):
    x = int((1 - avg_pos[0]) * width)
    y = int(avg_pos[1] * height)
    pygame.draw.circle(screen, (255, 0, 0), (x, y), 10)


def draw_landmarks(screen, result, width, height, avg_positions=None):
    if not result.hand_landmarks:
        return

    colors = [
        ((0, 255, 0), (255, 0, 0)),
        ((0, 255, 255), (255, 255, 0)),
    ]

    for index, hand in enumerate(result.hand_landmarks):
        line_color, joint_color = colors[index % len(colors)]
        _draw_single_hand(screen, hand, width, height, line_color, joint_color)

    if avg_positions:
        for avg_pos in avg_positions:
            _draw_average_position(screen, avg_pos, width, height)
