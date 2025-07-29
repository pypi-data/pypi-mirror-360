import torch
import pytest
from voidwalker import Voidwalker


def make_points(n=50, d=2, seed=42):
    torch.manual_seed(seed)
    return torch.rand(n, d)


def test_initialisation_and_run_with_implicit_bounds():
    points = make_points()
    vw = Voidwalker(points, n_samples=1000, n_voids=5, margin=1e-3,
                    outer_ring_width=0.05, alpha=0.05)
    voids, radii = vw.run()

    assert voids.shape == (5, 3)
    assert radii.shape == (5,)
    assert torch.all(voids[:, 2] > 0)
    assert torch.all(voids[:, 2] == radii)

    # Check memberships
    assert vw.memberships is not None
    assert isinstance(vw.memberships, list)
    assert len(vw.memberships) == 5

    # Check termination_reason contains only valid codes: 0, 1, 2
    assert vw.termination_reason.shape == (5,)
    assert torch.all((vw.termination_reason == 0) | (vw.termination_reason == 1) | (vw.termination_reason == 2))




def test_initialisation_and_run_with_explicit_bounds():
    points = make_points()
    vw = Voidwalker(points, n_samples=1000, n_voids=5, margin=1e-3,
                    outer_ring_width=0.05, alpha=0.05)
    voids, radii = vw.run()

    assert voids.shape == (5, 3)
    assert radii.shape == (5,)
    assert torch.all(voids[:, 2] > 0)

    # Check memberships
    assert vw.memberships is not None
    assert isinstance(vw.memberships, list)
    assert len(vw.memberships) == 5

    # Check termination_reason contains valid codes
    assert vw.termination_reason.shape == (5,)
    assert torch.all((vw.termination_reason == 0) | (vw.termination_reason == 1) | (vw.termination_reason == 2))


def test_voids_respect_bounds():
    points = make_points()
    vw = Voidwalker(points, n_samples=1000, n_voids=5, margin=1e-3, outer_ring_width=0.05, alpha=0.05)
    voids, _ = vw.run()

    centres = voids[:, :2]
    lower = vw.bounds[:, 0]
    upper = vw.bounds[:, 1]

    assert torch.all(centres >= lower)
    assert torch.all(centres <= upper)


def test_voids_approximately_repel_points():
    points = make_points()

    vw = Voidwalker(points, n_samples=1000, n_voids=5, margin=1e-3,)
    voids, radii, _ = vw.run()

    centres = voids[:, :2]
    dists = torch.cdist(centres, points)
    min_dists = dists.min(dim=1).values

    num_violations = (min_dists <= radii + 1e-3).sum().item()
    assert num_violations <= 1


def test_voids_approximately_repel_each_other():
    points = make_points()
    vw = Voidwalker(points, n_samples=1000, n_voids=6,
                                     margin=1e-3, outer_ring_width=0.05, alpha=0.05)

    voids, radii, _ = vw.run()

    centres = voids[:, :2]
    dists = torch.cdist(centres, centres)
    rr_sum = radii.unsqueeze(1) + radii.unsqueeze(0) + 1e-3
    eye = torch.eye(len(centres), dtype=torch.bool)
    close_pairs = (dists < rr_sum) & (~eye)
    too_close = close_pairs.any(dim=1)
    assert too_close.sum().item() <= 1


def test_high_margin_blocks_growth():
    points = make_points()
    with pytest.raises(RuntimeError, match="Not enough valid initial voids after filtering."):
        Voidwalker(points, n_samples=1000, n_voids=3,
                       margin=0.5, outer_ring_width=0.05, alpha=0.05).run()


def test_failure_when_no_valid_seeds():
    points = make_points(n=1000)
    with pytest.raises(RuntimeError, match="Not enough valid initial voids after filtering."):
        Voidwalker(points, n_samples=1000, n_voids=10,
                       margin=0.1, outer_ring_width=0.05, alpha=0.05).run()


def test_does_not_mutate_input_points():
    points = make_points()
    points_clone = points.clone()
    Voidwalker(points, n_samples=1000, n_voids=5,
                             margin=1e-3, outer_ring_width=0.05, alpha=0.05).run()
    assert torch.equal(points, points_clone)


def test_voids_terminate_by_csr_test():
    points = make_points(n=500)
    alpha = 0.05
    vw = Voidwalker(points, n_samples=1000, n_voids=5, margin=1e-3,
                    outer_ring_width=0.1, alpha=alpha)
    vw.run()

    member_counts = torch.tensor([len(m) for m in vw.memberships], dtype=torch.float32)
    radii = vw.voids[:, 2]
    expected_counts = vw.global_density * torch.pi * (
        (radii + vw.outer_ring_width) ** 2 - radii ** 2
    )

    k = member_counts.floor()
    lam = expected_counts.clamp(min=1e-8)
    cdf = torch.special.gammainc(k + 1, lam)
    p_values = 1.0 - cdf

    terminated = (p_values <= alpha)

    # Ensure termination_reason correctly tags these as csr_test
    assert torch.all(vw.termination_reason[terminated] == 0)

    # Remaining voids must be terminated by max_failures or max_steps
    other_terminated = (~terminated)
    assert torch.all((vw.termination_reason[other_terminated] == 1) | (vw.termination_reason[other_terminated] == 2))

