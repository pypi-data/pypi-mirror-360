import torch
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from voidwalker import Voidwalker

# Parameters
torch.manual_seed(42)
bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]], dtype=torch.float32)
n_polygons = 2
n_voids = 30  # reduced to avoid memory overload in animation
n_samples = 1000
margin = 0.01

# Step 1: Generate 3×3 grid of octagon centres
def generate_octagon_grid_centres(rows=3, cols=3, padding=0.15):
    x_lin = torch.linspace(padding, 1 - padding, steps=cols)
    y_lin = torch.linspace(padding, 1 - padding, steps=rows)
    grid_x, grid_y = torch.meshgrid(x_lin, y_lin, indexing='xy')
    centres = torch.stack([grid_x.flatten(), grid_y.flatten()], dim=1)
    return centres

# Step 2: Generate 8-sided regular polygons (octagons)
def generate_regular_octagon_vertices(centres, radius):
    theta = torch.linspace(0, 2 * torch.pi, steps=8 + 1)[:-1]
    offsets = torch.stack([radius * torch.cos(theta), radius * torch.sin(theta)], dim=1)
    boundary_points = []
    for c in centres:
        vertices = c.unsqueeze(0) + offsets
        boundary_points.append(vertices)
    return torch.cat(boundary_points, dim=0)

# Parameters for 3×3 grid
polygon_radius = 0.1
polygon_centres = generate_octagon_grid_centres(rows=3, cols=3, padding=0.15)
boundary_points = generate_regular_octagon_vertices(polygon_centres, polygon_radius)


# Step 3: Run Voidwalker and record frames
vw = Voidwalker(
    points=boundary_points,
    n_samples=n_samples,
    n_voids=n_voids,
    margin=margin,
    growth_step=1e-3,
    move_step=5e-3,
    max_steps=500,  # keep low for animation
    max_failures=50,
    outer_ring_width=0.02,
    alpha=0.05,
    record_frames=True
)

voids, radii, frames = vw.run()

# Step 4: Animate
fig, ax = plt.subplots(figsize=(6, 6))
sc_points = ax.scatter(boundary_points[:, 0], boundary_points[:, 1], c='black', s=1, label='Polygon Vertices')
circle_artists = []

def init():
    ax.set_xlim(bounds[0].tolist())
    ax.set_ylim(bounds[1].tolist())
    ax.set_aspect('equal')
    ax.set_title("Voidwalker Expansion Around Polygon Vertices")
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

# Save to file
gif_path = "/Users/jackpeyton/Documents/Voidwalker/testing/voidwalker_polygon_hypotest.gif"
ani.save(gif_path, writer='pillow', fps=10)
print(f"Animation saved to {gif_path}")
