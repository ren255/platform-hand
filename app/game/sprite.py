import pygame
from enum import Enum, auto

SHEET_PATH = "app/assets/pomni_sprite.png"
COLS = 8
ROWS = 6
CELL_W = 48
CELL_H = 64


class Direction(Enum):
    FRONT = auto()
    FRONT_LEFT = auto()
    FRONT_RIGHT = auto()  # 実データなし。FRONT_LEFTをミラーして使う
    BACK = auto()
    BACK_LEFT = auto()
    BACK_RIGHT = auto()  # 実データなし。BACK_LEFTをミラーして使う
    LEFT = auto()
    RIGHT = auto()


ROW_TO_DIRECTION = {
    0: Direction.FRONT_LEFT,
    1: Direction.FRONT,
    2: Direction.BACK_LEFT,
    3: Direction.BACK,
    4: Direction.LEFT,
    5: Direction.RIGHT,
}

MIRROR_SOURCE = {
    Direction.FRONT_RIGHT: Direction.FRONT_LEFT,
    Direction.BACK_RIGHT: Direction.BACK_LEFT,
}


class SpriteAnimation:
    """
    frames[0] は停止(idle)フレームでサイクルに含めない。
    frames[1:] をループ再生する。
    """

    def __init__(self, frames, fps=8):
        self.stop_frame = frames[0]
        self.cycle_frames = frames[1:]
        self.frame_duration = 1.0 / fps
        self.timer = 0.0
        self.index = 0
        self.playing = False

    def play(self):
        self.playing = True

    def stop(self):
        self.playing = False
        self.timer = 0.0
        self.index = 0

    def update(self, dt):
        if not self.playing or not self.cycle_frames:
            return
        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer -= self.frame_duration
            self.index = (self.index + 1) % len(self.cycle_frames)

    def current_frame(self):
        if self.playing and self.cycle_frames:
            return self.cycle_frames[self.index]
        return self.stop_frame


def _load_sheet(path):
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            rect = pygame.Rect(c * CELL_W, r * CELL_H, CELL_W, CELL_H)
            row.append(sheet.subsurface(rect).copy())
        frames.append(row)
    return frames


def _align_rows(frames):
    """行(アニメーション)ごとに平均重心を48/2へ合わせる。相対位置は維持。"""
    aligned = []
    for row in frames:
        centroids = []
        for f in row:
            mask = pygame.mask.from_surface(f)
            if mask.count() > 0:
                cx, _cy = mask.centroid()
            else:
                cx = CELL_W / 2
            centroids.append(cx)

        avg_cx = sum(centroids) / len(centroids)
        offset = round(CELL_W / 2 - avg_cx)

        new_row = []
        for f in row:
            new_surf = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
            new_surf.blit(f, (offset, 0))
            new_row.append(new_surf)
        aligned.append(new_row)
    return aligned


def load_player_animations(path=SHEET_PATH, fps=8):
    """
    スプライトシートを読み込み、Direction -> SpriteAnimation の辞書を返す。
    FRONT_RIGHT / BACK_RIGHT はミラー元フレームを反転して生成する。
    """
    raw_frames = _load_sheet(path)
    aligned_frames = _align_rows(raw_frames)

    animations = {}
    for row_index, direction in ROW_TO_DIRECTION.items():
        animations[direction] = SpriteAnimation(aligned_frames[row_index], fps=fps)

    for direction, source_direction in MIRROR_SOURCE.items():
        source_row = None
        for row_index, d in ROW_TO_DIRECTION.items():
            if d == source_direction:
                source_row = row_index
                break
        mirrored_frames = [
            pygame.transform.flip(f, True, False) for f in aligned_frames[source_row]
        ]
        animations[direction] = SpriteAnimation(mirrored_frames, fps=fps)

    return animations
