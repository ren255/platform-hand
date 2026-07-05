# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

from app.config import FLICK_ACCELERATION as THRESHOLD

MIN_TICK_GAP = 1
WINDOW = 11
POLY = 3

df = pd.read_csv("app/data/movement.csv")
df["ax"] = df["ax"].where(df["ax"].abs() <= 200, 0)
df = df.drop(df[df["ax"] == 0.0].index)


# %%
t = df["timestamp"].values - df["timestamp"].values[0]
dx = df["dx_cm"].values
right = df["right"].astype(bool).values
left = df["left"].astype(bool).values

dx_smooth = savgol_filter(dx, window_length=WINDOW, polyorder=POLY)
speed = np.gradient(dx_smooth, t)
accel = df["ax"].values


def get_edge_ticks(flag, min_gap):
    ticks = []
    last_tick = -min_gap
    for i in range(1, len(flag)):
        if flag[i] and not flag[i - 1]:
            if i - last_tick >= min_gap:
                ticks.append(i)
                last_tick = i
    return ticks


right_ticks = get_edge_ticks(right, MIN_TICK_GAP)
left_ticks = get_edge_ticks(left, MIN_TICK_GAP)

fig, axes = plt.subplots(3, 1, sharex=True, figsize=(12, 8))

labels = ["dx (cm)", "speed (cm/s)", "acceleration (cm/s²)"]
data = [dx_smooth, speed, accel]

for ax, d, label in zip(axes, data, labels):
    ax.plot(t, d, color="black", linewidth=1)
    ax.set_ylabel(label)
    for i in right_ticks:
        ax.axvline(t[i], color="red", linewidth=1)
    for i in left_ticks:
        ax.axvline(t[i], color="blue", linewidth=1)
    ax.grid(True, alpha=0.3)

axes[2].axhline(THRESHOLD, color="gray", linestyle="--", linewidth=1)
axes[2].axhline(-THRESHOLD, color="gray", linestyle="--", linewidth=1)

axes[-1].set_xlabel("time (s)")
fig.suptitle("Hand Movement: Position / Speed / Acceleration (smoothed)")
plt.tight_layout()
plt.savefig("movement_plot.png", dpi=150)
plt.show()
