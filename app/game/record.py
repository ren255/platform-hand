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
        if frame_bytes is None:  # 終了シグナル
            break
        proc.stdin.write(frame_bytes)

    proc.stdin.close()
    proc.wait()


class Recorder:
    def __init__(self, WINDOW_W, WINDOW_H, FPS, filename="record/output.mp4"):
        print(f"Recording to {filename} at {WINDOW_W}x{WINDOW_H} {FPS}fps")
        # バッファ上限（2秒分くらい）。無制限にするとメモリが際限なく増える可能性あり
        self.queue = mp.Queue(maxsize=int(FPS * 2))
        self.process = mp.Process(
            target=_writer_process,
            args=(self.queue, WINDOW_W, WINDOW_H, FPS, filename),
            daemon=True,
        )
        self.process.start()

    def capture_frame(self, surface):
        # array3d + transpose より tostring の方が軽い
        frame_bytes = pygame.image.tostring(surface, "RGB")
        self.queue.put(frame_bytes)

    def release(self):
        self.queue.put(None)
        self.process.join()
