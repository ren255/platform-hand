import os

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
GESTURE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/"
    "gesture_recognizer/float16/1/gesture_recognizer.task"
)
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "hand_landmarker.task")
GESTURE_MODEL_PATH = os.path.join(MODEL_DIR, "gesture_recognizer.task")

# Control settings
CONTROL_HAND = "Left"  # "Left" or "Right"
CALIBRATION_HOLD_MS = 1000
REFERENCE_DISTANCE_CM = 8.5
