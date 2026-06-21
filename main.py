import os
import sys
import time
import urllib.request

import cv2
import mediapipe as mp
import pygame
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.core.base_options import BaseOptions

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")

# 21-point hand connections (same topology as the old HAND_CONNECTIONS)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (5, 9), (9, 10), (10, 11), (11, 12),     # middle
    (9, 13), (13, 14), (14, 15), (15, 16),   # ring
    (13, 17), (17, 18), (18, 19), (19, 20),  # pinky
    (0, 17),
]


def ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading hand_landmarker.task model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded.")


class HandTracker:
    def __init__(self, max_hands=1):
        ensure_model()
        options = mp_vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = mp_vision.HandLandmarker.create_from_options(options)
        self._start_time = time.time()

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.time() - self._start_time) * 1000)
        return self.landmarker.detect_for_video(mp_image, timestamp_ms)

    def close(self):
        self.landmarker.close()


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