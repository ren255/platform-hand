import time
import pygame
import subprocess
import multiprocessing as mp
from pathlib import Path


def _writer_process(queue: mp.Queue, WINDOW_W, WINDOW_H, FPS, filename):
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
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
        "-",
        "-an",
        "-vcodec",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "ultrafast",
        filename,
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    while True:
        frame_bytes = queue.get()
        if frame_bytes is None:
            break
        proc.stdin.write(frame_bytes)

    proc.stdin.close()
    proc.wait()


class Recorder:
    """1プロセス内で完結して使う。プロセス境界を越えて渡さない。"""

    def __init__(self, WINDOW_W, WINDOW_H, FPS, filename="record/output.mp4"):
        self.WINDOW_W = WINDOW_W
        self.WINDOW_H = WINDOW_H
        self.FPS = FPS
        self.filename = filename

        self.queue = None
        self.process = None
        self.start_time = None
        self.frames_written = 0

    def start(self, start_time: float):
        print(
            f"Recording to {self.filename} at {self.WINDOW_W}x{self.WINDOW_H} {self.FPS}fps"
        )
        self.queue = mp.Queue(maxsize=int(self.FPS * 2))
        self.process = mp.Process(
            target=_writer_process,
            args=(self.queue, self.WINDOW_W, self.WINDOW_H, self.FPS, self.filename),
            daemon=True,
        )
        self.process.start()
        self.start_time = start_time
        self.frames_written = 0

    def capture_frame(self, surface):
        frame_bytes = pygame.image.tostring(surface, "RGB")
        now = time.monotonic()

        target_frame_count = int((now - self.start_time) * self.FPS) + 1
        if target_frame_count <= self.frames_written:
            return  # 呼び出しが速すぎる分は間引く

        n_to_write = target_frame_count - self.frames_written  # 遅延分は複製で埋める
        for _ in range(n_to_write):
            self.queue.put(frame_bytes)
        self.frames_written = target_frame_count

    def stop(self):
        if self.process is None:
            return
        self.queue.put(None)
        self.process.join()
        self.process = None
        self.queue = None
