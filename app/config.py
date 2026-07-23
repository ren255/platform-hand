import os

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
GESTURE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/"
    "gesture_recognizer/float16/1/gesture_recognizer.task"
)
MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model"
)
MODEL_PATH = os.path.join(MODEL_DIR, "hand_landmarker.task")
GESTURE_MODEL_PATH = os.path.join(MODEL_DIR, "gesture_recognizer.task")

# Control settings
CONTROL_HAND = "Right"  # "Left" or "Right"
CALIBRATION_HOLD_MS = 1000
REFERENCE_DISTANCE_CM = 7
WASD = True  # Enable WASD input in addition to arrow-style directions
DEADZONE_CM = 2
MAX_HAND_SPEED = 0.5  # hand speed that will be mapped to max player speed

# Flick detection / hand input smoothing
HAND_EMA_ALPHA = 0.6  # EMA smoothing factor (0..1)
FLICK_MIN_SPEED = 0.7  # cm/s, minimum hand speed to trigger a flick
FLICK_MIN_ACCELERATION = 50  # cm/s^2, minimum hand acceleration to trigger a flick
FLICK_MAX_ACCELERATION = 100.0  # cm/s^2, anomaly rejection upper bound for acceleration

MOVE_SPEED = 300
GRAVITY = 1500
JUMP_SPEED = -800
MAX_FALL_SPEED = 300

HAND_INPUT_METHOD = "acceleration"  # speed/acceleration or distance
WINDOW_W, WINDOW_H = 1500, 800

RECORD = False
FPS = 60
