import math
import time

from app.config import CALIBRATION_HOLD_MS, CONTROL_HAND, REFERENCE_DISTANCE_CM
from app.hand.gesture import HandGesture


class HandController:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # 初期原点は画面中央（正規化座標）
        self.origin = (0.5, 0.5)
        self.cm_per_px = None
        self._calibration_start = None
        self._calibration_positions = []
        self.last_time = time.time()
        self.last_pos = [0,0]

    def _find_control_hand(self, hands):
        """configで指定した手を探す。"""
        for gesture, avg_pos, label in hands:
            if label == CONTROL_HAND:
                return gesture, avg_pos, label
        return None

    def _find_control_landmarks(self, result):
        """configで指定した手のランドマークを探す。"""
        if not result.hand_landmarks:
            return None
        for hand_landmarks, handedness in zip(result.hand_landmarks, result.handedness):
            label = handedness[0].category_name if handedness else "Unknown"
            if label == CONTROL_HAND:
                return hand_landmarks
        return None

    def _distance_px(self, p1, p2):
        dx = (p1[0] - p2[0]) * self.width
        dy = (p1[1] - p2[1]) * self.height
        return math.hypot(dx, dy)

    def update(self, result, hands):
        control = self._find_control_hand(hands)
        if control is None:
            self._calibration_start = None
            self._calibration_positions = []
            return self._output(HandGesture.UNKNOWN)

        gesture, avg_pos, _ = control

        if gesture == HandGesture.ROCK_ON:
            self._calibration_positions.append(avg_pos)
            if self._calibration_start is None:
                self._calibration_start = time.time()
            elapsed_ms = (time.time() - self._calibration_start) * 1000
            if elapsed_ms >= CALIBRATION_HOLD_MS and self._calibration_positions:
                # 新しい原点をキャリブレーション中の平均位置に設定
                ox = sum(p[0] for p in self._calibration_positions) / len(self._calibration_positions)
                oy = sum(p[1] for p in self._calibration_positions) / len(self._calibration_positions)
                self.origin = (ox, oy)
                # スケール計算: 人差し指先端(8)と小指先端(20)の距離
                hand = self._find_control_landmarks(result)
                if hand:
                    index_tip = (hand[8].x, hand[8].y)
                    pinky_tip = (hand[20].x, hand[20].y)
                    dist_px = self._distance_px(index_tip, pinky_tip)
                    if dist_px > 0:
                        self.cm_per_px = REFERENCE_DISTANCE_CM / dist_px
                self._calibration_start = None
                self._calibration_positions = []
        else:
            self._calibration_start = None
            self._calibration_positions = []

  
        return self._output(gesture, avg_pos)

    def _output(self, state, avg_pos=None):
        origin_px = (self.width - int(self.origin[0] * self.width), int(self.origin[1] * self.height))
        if avg_pos is None:
            return {
                "state": state,
                "relative_cm": (0.0, 0.0),
                "origin_px": origin_px,
                "speed": (0,0),
            }

        dx_px = (avg_pos[0] - self.origin[0]) * self.width * -1
        dy_px = (avg_pos[1] - self.origin[1]) * self.height
        if self.cm_per_px is not None:
            dx_cm = dx_px * self.cm_per_px
            dy_cm = dy_px * self.cm_per_px
        else:
            dx_cm = 0.0
            dy_cm = 0.0
            
        speed_x = (  self.last_pos[0] - avg_pos[0]) / (time.time() - self.last_time)
        speed_y = (  self.last_pos[1] - avg_pos[1]) / (time.time() - self.last_time)
        
        self.last_pos[0], self.last_pos[1] = avg_pos[0] , avg_pos[1]
        self.last_time = time.time()

        return {
            "state": state,
            "relative_cm": (dx_cm, dy_cm),
            "origin_px": origin_px,
            "speed": (speed_x,speed_y),
        }
