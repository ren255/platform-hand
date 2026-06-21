import sys

import cv2
import mediapipe as mp
import pygame


class HandTracker:
    def __init__(self, max_hands=1):
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.connections = mp.solutions.hands.HAND_CONNECTIONS

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb)

    def close(self):
        self.hands.close()


def frame_to_surface(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = cv2.flip(rgb, 1)
    return pygame.surfarray.make_surface(rgb.swapaxes(0, 1))


def draw_landmarks(screen, result, width, height):
    if not result.multi_hand_landmarks:
        return

    for hand in result.multi_hand_landmarks:
        points = [
            (int(lm.x * width), int(lm.y * height)) for lm in hand.landmark
        ]

        for connection in mp.solutions.hands.HAND_CONNECTIONS:
            start, end = connection
            pygame.draw.line(screen, (0, 255, 0), points[start], points[end], 2)

        for x, y in points:
            pygame.draw.circle(screen, (255, 0, 0), (x, y), 5)


def main():
    pygame.init()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not found")
        sys.exit(1)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    tracker = HandTracker()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

        ok, frame = cap.read()
        if not ok:
            continue

        result = tracker.process(frame)
        surface = frame_to_surface(frame)
        screen.blit(surface, (0, 0))
        draw_landmarks(screen, result, width, height)
        pygame.display.flip()

        clock.tick(30)

    tracker.close()
    cap.release()
    pygame.quit()


if __name__ == "__main__":
    main()
