# System Overview

This document explains the code structure of `platform-hand`, a platformer game controlled by hand gestures.

## Directory Layout

```
.
├── app/
│   ├── __init__.py
│   ├── config.py          # Shared configuration (model URL/path)
│   ├── game/              # Game application code. not implemented.
│   │   ├── __init__.py
│   │   ├── app.py         
│   │   ├── level.py       
│   │   ├── physics.py     
│   │   ├── player.py      
│   │   └── renderer.py    
│   └── hand/              # Hand tracking code
│       ├── __init__.py
│       ├── camera.py      # Camera + MediaPipe hand tracker
│       ├── gesture.py     # Gesture interpretation (placeholder)
│       ├── test_run.py    # Standalone camera/hand test
│       └── renderer.py    # render the hand
├── model/
│   └── hand_landmarker.task   # MediaPipe hand landmarker model
├── main.py                # Legacy entry point (kept for reference)
├── pyproject.toml
├── README.md
└── SYSTEM.md              # This file
```

## Modules

### `app.config`

Central configuration for the project. It defines:

- `MODEL_URL`: URL to download the MediaPipe `hand_landmarker.task` model.
- `MODEL_DIR`: Local directory for the model (`./model/`).
- `MODEL_PATH`: Full path to the model file.

### `app.hand.camera`

Handles computer vision and hand tracking.

- `ensure_model()`: Downloads the MediaPipe model if it is not already present.
- `Camera`: Wraps `cv2.VideoCapture` to read frames from the webcam.
- `HandTracker`: Loads the MediaPipe hand landmarker and runs detection on frames.
- `HAND_CONNECTIONS`: Skeleton connections used to draw the hand.

### `app.hand.test_run`

A small standalone script for camera and hand tracker work without starting the full game.
Run it with:

```sh
python -m app.hand.test_run
```

### `app.game.renderer`

Pygame-specific rendering helpers.

- `frame_to_surface(frame)`: Converts an OpenCV BGR frame into a flipped Pygame surface.
- `draw_landmarks(screen, result, width, height)`: Draws detected hand landmarks and skeleton on the screen.

### `app.game.app`

The main game application. It initializes Pygame, opens the camera, runs the hand tracker, and renders the camera feed with landmarks overlaid.

Entry point after installation:

```sh
platform-hand
```

Or directly:

```sh
python -m app.game.app
```

## Data Flow

1. `app.game.app` initializes Pygame and the `Camera`.
2. Each frame is read from `Camera`.
3. `HandTracker.process(frame, timestamp_ms)` runs MediaPipe inference.
4. `renderer.frame_to_surface(frame)` converts the frame for Pygame.
5. `renderer.draw_landmarks(...)` overlays the hand skeleton.
6. The result is blitted onto the screen.

level.py: 

LEVEL =[

[
]
]

class LevelManager:


player に collision check追加
- for BLOCK color check
red:自殺
green: next state


松若メモ

プログラムのコミット:
git push --set-upstream origin feat/game         
git push