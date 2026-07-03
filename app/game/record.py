import pygame
import numpy as np
import subprocess

from pathlib import Path


class Recorder:
    def __init__(self, WINDOW_W, WINDOW_H, FPS, filename="record/output.mp4"):
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        ffmpeg_cmd = [
            "ffmpeg",
            "-y",  # 上書き許可
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-s",
            f"{WINDOW_W}x{WINDOW_H}",
            "-pix_fmt",
            "rgb24",
            "-r",
            str(FPS),
            "-i",
            "-",  # 標準入力から読む
            "-an",  # 音声なし
            "-vcodec",
            "libx264",  # ソフトウェアエンコーダを明示指定
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "ultrafast",
            filename,
        ]

        self.proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    def capture_frame(self, surface):
        # pygame surface -> numpy配列 (幅,高さ,RGB) -> ffmpegへ(H,W,RGB)で流す
        frame = pygame.surfarray.array3d(surface)
        frame = np.transpose(frame, (1, 0, 2))  # (W,H,3) -> (H,W,3)
        self.proc.stdin.write(frame.tobytes())

    def release(self):
        self.proc.stdin.close()
        self.proc.wait()
