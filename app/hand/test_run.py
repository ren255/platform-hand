import sys
import time

import cv2
import pygame

from app.hand.camera import Camera, GestureTracker
from app.hand.gesture import recognize_hands
from app.hand.renderer import draw_landmarks, frame_to_surface


def _draw_gesture_label(screen, text, position, font, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


def main():
    pygame.init()

    camera = Camera()
    width, height = camera.width, camera.height
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    tracker = GestureTracker()
    start_time = time.time()
    font = pygame.font.SysFont(None, 48)

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

        surface = frame_to_surface(frame)
        screen.blit(surface, (0, 0))

        avg_positions = [avg_pos for _, avg_pos, _ in hands]
        draw_landmarks(screen, result, width, height, avg_positions)

        # 左右の手のジェスチャーを画面下に表示
        for gesture, avg_pos, label in hands:
            text = gesture.name
            text_surface = font.render(text, True, (255, 255, 255))
            if label == "Right":
                text_x = width - text_surface.get_width() - 20
            else:
                text_x = 20
            _draw_gesture_label(screen, text, (text_x, height - 60), font)

        pygame.display.flip()

        clock.tick(30)

    tracker.close()
    camera.release()
    pygame.quit()


if __name__ == "__main__":
    main()
