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
CONTROL_HAND = "Right"  # "Left" or "Right"
CALIBRATION_HOLD_MS = 1000
REFERENCE_DISTANCE_CM = 7
WASD = True  # Enable WASD input in addition to arrow-style directions
DEADZONE_CM = 2
MAX_HAND_SPEED = 1 # hand speed that will be mapped to max player speed

MOVE_SPEED = 6      # horizontal pixels per frame
GRAVITY = 0.6        # vertical acceleration per frame
JUMP_SPEED = -11.0    # initial upward velocity on jump
MAX_FALL_SPEED = 15.0

HAND_INPUT_METHOD = "speed" # speed or distance

WINDOW_W, WINDOW_H = 640, 480
