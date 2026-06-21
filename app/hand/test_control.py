import math
import sys
import time

import cv2
import pygame

from app.config import CALIBRATION_HOLD_MS, CONTROL_HAND
from app.hand.camera import Camera, GestureTracker
from app.hand.controller import HandController
from app.hand.gesture import recognize_hands
from app.hand.renderer import draw_landmarks, frame_to_surface,draw_origin_cross


def _draw_text(screen, text, position, font, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


def main():
    pygame.init()

    camera = Camera()
    width, height = camera.width, camera.height
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    tracker = GestureTracker()
    controller = HandController(width, height)
    start_time = time.time()
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)

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
        hands = recognize_hands(result)
        control = controller.update(result, hands)

        surface = frame_to_surface(frame)
        screen.blit(surface, (0, 0))

        avg_positions = [avg_pos for _, avg_pos, _ in hands]
        draw_landmarks(screen, result, width, height, avg_positions)
        draw_origin_cross(screen,control["origin_px"])

        for gesture, avg_pos, label in hands:
            text = gesture.name
            # CONTROL_HANDは緑色
            if label == CONTROL_HAND:
                color = (0, 255, 0)
            else:
                color = (255, 255, 255)
            text_surface = font.render(text, True, color)
            if label == "Right":
                text_x = width - text_surface.get_width() - 20
            else:
                text_x = 20
            _draw_text(screen, text, (text_x, height - 60), font, color)


        # 原点相対距離（cm）を画面下側中央に表示
        dx_cm, dy_cm = control["relative_cm"]
        cm_text = f"x: {dx_cm:+.1f}cm  y: {dy_cm:+.1f}cm"
        text_surface = small_font.render(cm_text, True, (255, 255, 255))
        text_x = (width - text_surface.get_width()) // 2
        text_y = height - text_surface.get_height() - 30
        _draw_text(screen, cm_text, (text_x, text_y), small_font)

        pygame.display.flip()

        clock.tick(30)

    tracker.close()
    camera.release()
    pygame.quit()


if __name__ == "__main__":
    main()
