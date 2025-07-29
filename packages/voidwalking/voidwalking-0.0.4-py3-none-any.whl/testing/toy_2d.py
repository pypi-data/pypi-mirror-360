import torch
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from voidwalker import Voidwalker

# Create toy point cloud
torch.manual_seed(42)
points = torch.rand(500, 2)
bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]], dtype=torch.float32)

# Run real Voidwalker and record internal frames
n_voids = 200
n_samples = 10000
margin = 0.001

vw = Voidwalker(
    points,
    n_samples=n_samples,
    n_voids=n_voids,
    margin=margin,
    move_step=0.001,
    growth_step=0.0005,
    max_steps=10000,
    max_failures=50,
    outer_ring_width=0.002,
    alpha=0.05,
    record_frames=True
)

voids, radii, frames = vw.run()

# Plotting setup
fig, ax = plt.subplots(figsize=(6, 6))
sc_points = ax.scatter(points[:, 0], points[:, 1], c='black', s=10, label='Points')
circle_artists = []

def init():
    ax.set_xlim(bounds[0].tolist())
    ax.set_ylim(bounds[1].tolist())
    ax.set_aspect('equal')
    ax.set_title("Voidwalker Growth and Repulsion (Real Output)")
    return []

def update(frame):
    global circle_artists
    for artist in circle_artists:
        artist.remove()
    circle_artists = []

    centres, radii = frame
    for c, r in zip(centres, radii):
        circle = plt.Circle(c.tolist(), r.item(), edgecolor='blue', facecolor='none', linewidth=1.0)
        ax.add_patch(circle)
        circle_artists.append(circle)
    return circle_artists

ani = animation.FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=100)

# Save to local path
gif_path = "/Users/jackpeyton/Documents/Voidwalker/testing/voidwalker_growth_hypotest.gif"
ani.save(gif_path, writer='pillow', fps=10)
