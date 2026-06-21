from enum import Enum, auto


class HandGesture(Enum):
    UNKNOWN = auto()
    NONE = auto()
    OPEN = auto()        # Open_Palm
    FIST = auto()        # Closed_Fist
    PEACE = auto()       # Victory
    POINTING = auto()    # Pointing_Up
    THUMBS_UP = auto()   # Thumb_Up
    THUMBS_DOWN = auto() # Thumb_Down
    ROCK_ON = auto()     # ILoveYou


_GESTURE_MAP = {
    "None": HandGesture.NONE,
    "Open_Palm": HandGesture.OPEN,
    "Closed_Fist": HandGesture.FIST,
    "Victory": HandGesture.PEACE,
    "Pointing_Up": HandGesture.POINTING,
    "Thumb_Up": HandGesture.THUMBS_UP,
    "Thumb_Down": HandGesture.THUMBS_DOWN,
    "ILoveYou": HandGesture.ROCK_ON,
}


def _average_position(hand):
    avg_x = sum(lm.x for lm in hand) / len(hand)
    avg_y = sum(lm.y for lm in hand) / len(hand)
    return avg_x, avg_y


def _mirrored_label(label):
    """MediaPipeのhandednessは元画像基準。画面は左右反転しているのでラベルを反転する。"""
    return "Right" if label == "Left" else "Left"


def recognize_hands(result):
    """GestureRecognizerの結果から、各手のジェスチャーと平均位置、左右ラベルを返す。

    返すラベルは画面表示（ミラー）に合わせて反転済み。
    """
    if not result.hand_landmarks:
        return []

    hands = []
    for hand_landmarks, gestures, handedness in zip(
        result.hand_landmarks, result.gestures, result.handedness
    ):
        name = gestures[0].category_name if gestures else "None"
        gesture = _GESTURE_MAP.get(name, HandGesture.UNKNOWN)
        avg_pos = _average_position(hand_landmarks)
        raw_label = handedness[0].category_name if handedness else "Unknown"
        label = _mirrored_label(raw_label)
        hands.append((gesture, avg_pos, label))
    return hands
