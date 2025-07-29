import torch
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from voidwalker import Voidwalker
import h5py
import numpy as np

# Set random seed and bounds
torch.manual_seed(42)
WINDOW = torch.tensor([[-500., 500.],
                       [-500., 500.]],
                      dtype=torch.float32)

# Load MINFLUX measurement data
file_path = '/Users/jackpeyton/Documents/RJMINFLUX/data/Nup96_sparse.h5'
with h5py.File(file_path, 'r') as file:
    measurement_positions = file['observed/position'][:, :2]
    measurement_positions = np.asarray(measurement_positions, dtype=np.float32)

Y = torch.tensor(measurement_positions, dtype=torch.float32)

# Run Voidwalker with frame recording
vw = Voidwalker(
    Y,
    n_samples=15_000,
    n_voids=150,
    margin=15,
    growth_step=2.5e-1,
    max_radius=50,
    initial_radius=10,
    move_step=1,
    max_steps=5_000,
    max_failures=50,
    outer_ring_width=5,
    alpha=0.05,
    record_frames=True
)

voids, radii, frames = vw.run()

# Create animation
fig, ax = plt.subplots(figsize=(7, 7))
ax.set_xlim(WINDOW[0].tolist())
ax.set_ylim(WINDOW[1].tolist())
ax.set_aspect('equal')
sc = ax.scatter(Y[:, 0], Y[:, 1], c='black', s=1, label='MINFLUX Points')
circle_artists = []

def init():
    ax.set_title("Voidwalker on MINFLUX Data")
    return []

def update(frame):
    global circle_artists
    for artist in circle_artists:
        artist.remove()
    circle_artists = []

    centres, radii = frame
    for c, r in zip(centres, radii):
        circle = plt.Circle(c.tolist(), r.item(), edgecolor='blue', facecolor='none', linewidth=0.8)
        ax.add_patch(circle)
        circle_artists.append(circle)
    return circle_artists

ani = animation.FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=100)

# Save the animation
gif_path = "/Users/jackpeyton/Documents/Voidwalker/testing/minflux_voidwalker_hypotest.gif"
ani.save(gif_path, writer='pillow', fps=10)
print(f"Saved GIF to {gif_path}")
