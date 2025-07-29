import torch
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
    growth_step=0.2,
    max_radius=50,
    initial_radius=10,
    move_step=0.5,
    max_steps=5_000,
    max_failures=50,
    outer_ring_width=30,
    alpha=0.05,
    record_frames=False
)

voids, radii, _ = vw.run()

print(vw.termination_reason)

for i, members in enumerate(vw.memberships):
    print(f"Void {i}: {len(members)} points -> {members.tolist()}")

all_members = torch.cat([m for m in vw.memberships if len(m) > 0])
unique_members = torch.unique(all_members)
print(f"Total unique member points: {len(unique_members)}")

import matplotlib.pyplot as plt

# Plot Y points
plt.figure(figsize=(8, 8))
plt.scatter(Y[:, 0], Y[:, 1], s=5, alpha=0.5, label='Points')

# Plot voids with colour based on termination reason
centres = voids[:, :2]
radii = radii.numpy()
termination = vw.termination_reason.numpy()

for centre, radius, reason in zip(centres, radii, termination):
    colour = 'blue' if reason == 0 else 'black'
    circle = plt.Circle(centre, radius, fill=False, linewidth=1.5, edgecolor=colour)
    plt.gca().add_patch(circle)

plt.title("MINFLUX Points and Final Voids (Blue = CSR Termination)")
plt.xlabel("X")
plt.ylabel("Y")
plt.axis("equal")
plt.legend()
plt.show()

# Identify non-member points
all_indices = torch.arange(Y.shape[0])
non_members = torch.tensor([i for i in all_indices if i not in unique_members])

plt.figure(figsize=(8, 8))
plt.scatter(Y[non_members, 0], Y[non_members, 1], s=5, c='red', alpha=0.6, label='Non-member points')
plt.scatter(Y[unique_members, 0], Y[unique_members, 1], s=5, c='blue', alpha=0.6, label='Member points')

# Plot voids
for centre, radius, reason in zip(centres, radii, termination):
    colour = 'blue' if reason == 0 else 'black'
    circle = plt.Circle(centre, radius, fill=False, linewidth=1.5, edgecolor=colour)
    plt.gca().add_patch(circle)

plt.title("MINFLUX Points: Red = Unexplained, Blue = Members, Circles = Voids")
plt.xlabel("X")
plt.ylabel("Y")
plt.axis("equal")
plt.legend()
plt.show()