import pygame
import cv2
import numpy as np

pygame.init()

WIDTH, HEIGHT = 640, 480
FPS = 30
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 動画ライター(mp4形式)の準備
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter('output.mp4', fourcc, FPS, (WIDTH, HEIGHT))

def capture_frame(surface, writer):
    # pygame surface -> numpy配列 (幅,高さ,RGB) -> OpenCV用に転置・BGR変換
    frame = pygame.surfarray.array3d(surface)
    frame = np.transpose(frame, (1, 0, 2))  # (W,H,3) -> (H,W,3)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    writer.write(frame)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- ここに通常の描画処理 ---
    screen.fill((30, 30, 30))
    pygame.draw.circle(screen, (255, 0, 0), (WIDTH // 2, HEIGHT // 2), 50)
    # --- 描画処理ここまで ---

    pygame.display.flip()

    # このフレームを録画
    capture_frame(screen, video_writer)

    clock.tick(FPS)

video_writer.release()
pygame.quit()