import os
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.core.base_options import BaseOptions

from app.config import (
    GESTURE_MODEL_PATH,
    GESTURE_MODEL_URL,
    MODEL_PATH,
    MODEL_URL,
)

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
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        print("Downloading hand_landmarker.task model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded.")


def ensure_gesture_model():
    if not os.path.exists(GESTURE_MODEL_PATH):
        os.makedirs(os.path.dirname(GESTURE_MODEL_PATH), exist_ok=True)
        print("Downloading gesture_recognizer.task model...")
        urllib.request.urlretrieve(GESTURE_MODEL_URL, GESTURE_MODEL_PATH)
        print("Model downloaded.")


class Camera:
    def __init__(self, device_index=0):
        self.cap = cv2.VideoCapture(device_index)
        if not self.cap.isOpened():
            raise RuntimeError("Camera not found")
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()


class GestureTracker:
    def __init__(self, max_hands=2):
        ensure_gesture_model()
        options = mp_vision.GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_path=GESTURE_MODEL_PATH),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=0.8,
            min_hand_presence_confidence=0.8,
            min_tracking_confidence=0.8,
        )
        self.recognizer = mp_vision.GestureRecognizer.create_from_options(options)

    def process(self, frame, timestamp_ms):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        return self.recognizer.recognize_for_video(mp_image, timestamp_ms)

    def close(self):
        self.recognizer.close()
