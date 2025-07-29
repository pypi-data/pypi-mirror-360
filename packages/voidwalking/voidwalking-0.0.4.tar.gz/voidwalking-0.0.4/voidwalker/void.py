import torch
from scipy.stats import poisson

class Voidwalker:
    def __init__(self, points, n_samples, n_voids, margin=10, initial_radius=1e-2, growth_step=1e-2, max_radius=None,
                 move_step=1e-1, max_steps=25_000, max_failures=10, outer_ring_width=10.0, alpha=0.05, record_frames=False):
        self.points = points
        self.n_voids = n_voids
        self.n_samples = n_samples

        min_vals = self.points.min(dim=0).values
        max_vals = self.points.max(dim=0).values
        self.bounds = torch.stack([min_vals, max_vals], dim=1)

        self.margin = margin
        self.growth_step = growth_step
        self.move_step = move_step
        self.max_steps = max_steps
        self.max_failures = max_failures
        self.max_radius = max_radius
        self.initial_radius = initial_radius
        self.outer_ring_width = outer_ring_width
        self.alpha = alpha
        self.memberships = None

        self.d = points.shape[1]
        self.voids = self._initialise_voids()
        self.active = torch.ones(n_voids, dtype=torch.bool)
        self.consec_failures = torch.zeros(n_voids, dtype=torch.int)
        self.termination_reason = torch.full((n_voids,), -1, dtype=torch.int)

        self.record_frames = record_frames
        self.frames = []

        area = torch.prod(self.bounds[:, 1] - self.bounds[:, 0])
        self.global_density = self.points.shape[0] / area

    def _record_frame(self):
        if self.record_frames:
            centres = self.voids[:, :self.d].clone()
            radii = self.voids[:, self.d].clone()
            self.frames.append((centres, radii))

    def _initialise_voids(self):
        candidates = torch.rand(self.n_samples, self.d) * (self.bounds[:, 1] - self.bounds[:, 0]) + self.bounds[:, 0]
        dists = torch.cdist(candidates, self.points)
        min_dists = dists.min(dim=1).values
        safe = min_dists > (self.initial_radius + self.margin)
        candidates = candidates[safe]
        scores = min_dists[safe]

        if len(candidates) < self.n_voids:
            raise RuntimeError("Not enough valid initial voids after filtering.")

        selected = [candidates[scores.argmax().item()]]
        candidates = torch.cat([candidates[:scores.argmax()], candidates[scores.argmax() + 1:]])

        for _ in range(1, self.n_voids):
            dists = torch.cdist(candidates, torch.stack(selected))
            min_dists = dists.min(dim=1).values
            idx = min_dists.argmax().item()
            selected.append(candidates[idx])
            candidates = torch.cat([candidates[:idx], candidates[idx + 1:]])
            if len(candidates) == 0:
                break

        if len(selected) < self.n_voids:
            raise RuntimeError("Failed to seed enough voids after maximin filtering.")

        centres = torch.stack(selected)
        radii = torch.full((self.n_voids, 1), self.initial_radius)
        return torch.cat([centres, radii], dim=1)

    def get_outer_ring_membership(self):
        centres = self.voids[:, :self.d]
        radii = self.voids[:, self.d]
        dists = torch.cdist(self.points, centres)

        inner_bounds = radii.unsqueeze(0)
        outer_bounds = (radii + self.outer_ring_width).unsqueeze(0)

        within_ring = (dists > inner_bounds) & (dists < outer_bounds)
        memberships = [torch.where(within_ring[:, i])[0] for i in range(self.n_voids)]
        return memberships

    def _point_distances(self, centres):
        return torch.cdist(centres, self.points)

    def _sample_directions(self):
        dirs = torch.randn(self.n_voids, self.d)
        return dirs / dirs.norm(dim=1, keepdim=True)

    def _can_grow_mask(self):
        centres = self.voids[:, :self.d]
        proposed_radii = self.voids[:, self.d] + self.growth_step
        dists = self._point_distances(centres)
        min_dists = dists.min(dim=1).values
        safe = min_dists > proposed_radii + self.margin

        if self.max_radius is not None:
            safe = safe & (proposed_radii <= self.max_radius)
        return safe

    def _can_move(self, new_centres):
        dists = torch.cdist(new_centres, self.points)
        radii = self.voids[:, self.d]
        min_dists = dists.min(dim=1).values
        within_bounds = ((new_centres >= self.bounds[:, 0]) & (new_centres <= self.bounds[:, 1])).all(dim=1)
        safe = min_dists > radii + self.margin
        return safe & within_bounds & self.active

    def _attempt_walk(self, mask=None):
        if mask is None:
            mask = self.active

        centres = self.voids[:, :self.d]
        radii = self.voids[:, self.d]
        vp_dists = torch.cdist(centres, self.points)
        vp_overlap = vp_dists < (radii.unsqueeze(1) + self.margin)
        vv_dists = torch.cdist(centres, centres)
        rr_sum = radii.unsqueeze(1) + radii + self.margin
        vv_overlap = (vv_dists < rr_sum) & (~torch.eye(self.n_voids, dtype=torch.bool))

        repulsion_vecs = torch.zeros_like(centres)

        for i in range(self.n_voids):
            if not mask[i]:
                continue

            repulsion = torch.zeros(self.d)
            offending_points = self.points[vp_overlap[i]]
            if len(offending_points) > 0:
                dirs = centres[i] - offending_points
                repulsion += (dirs / (dirs.norm(dim=1, keepdim=True) + 1e-8)).sum(dim=0)

            offending_voids = centres[vv_overlap[i]]
            if len(offending_voids) > 0:
                dirs = centres[i] - offending_voids
                repulsion += (dirs / (dirs.norm(dim=1, keepdim=True) + 1e-8)).sum(dim=0)

            if repulsion.norm() > 0:
                repulsion_vecs[i] = repulsion / repulsion.norm()
            else:
                repulsion_vecs[i] = torch.randn(self.d)
                repulsion_vecs[i] /= repulsion_vecs[i].norm()

        step = self.move_step * repulsion_vecs
        proposed = centres + step
        can_move = self._can_move(proposed)
        self.voids[can_move, :self.d] = proposed[can_move]

    def _attempt_grow(self):
        if not hasattr(self, 'csr_violated'):
            self.csr_violated = torch.zeros(self.n_voids, dtype=torch.bool)

        memberships = self.get_outer_ring_membership()
        member_counts = torch.tensor([len(m) for m in memberships], dtype=torch.float32)

        radii = self.voids[:, self.d]
        expected_counts = self.global_density * torch.pi * ((radii + self.outer_ring_width)**2 - radii**2)
        expected_counts = expected_counts.clamp(min=1e-8)

        p_values = 1.0 - torch.tensor(poisson.cdf(member_counts.numpy(), expected_counts.numpy()))
        new_csr_violations = (p_values <= self.alpha) & self.active & (~self.csr_violated)
        self.csr_violated |= new_csr_violations

        can_grow = self._can_grow_mask() & self.active
        self.voids[can_grow, self.d] += self.growth_step
        self.consec_failures[can_grow] = 0

        failed_to_grow = (~can_grow) & self.active
        self.consec_failures[failed_to_grow] += 1

        self._attempt_walk(mask=failed_to_grow)

        self.active = self.active & (self.consec_failures < self.max_failures)
        finalising_csr = self.csr_violated & (~self.active) & (self.termination_reason == -1)
        self.termination_reason[finalising_csr] = 0
        finalising_fail = (~self.csr_violated) & (~self.active) & (self.termination_reason == -1)
        self.termination_reason[finalising_fail] = 1

        self._record_frame()

    def run(self):
        for _ in range(self.max_steps):
            if not self.active.any():
                break
            self._attempt_grow()

        self.memberships = self.get_outer_ring_membership()
        still_active = self.active & (self.termination_reason == -1)
        self.termination_reason[still_active] = 2

        return self.voids, self.voids[:, self.d], self.frames if self.record_frames else None
