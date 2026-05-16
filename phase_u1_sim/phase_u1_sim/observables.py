from __future__ import annotations

import numpy as np
from .lattice import forward_diff, wrap_angle


def phase_correlation(theta: np.ndarray, max_r: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Radially averaged C(r)=<cos(theta(x+r)-theta(x))> along axes."""
    nx, ny = theta.shape
    if max_r is None:
        max_r = min(nx, ny) // 2
    rs = np.arange(max_r + 1)
    corr = np.empty_like(rs, dtype=float)
    for i, r in enumerate(rs):
        if r == 0:
            corr[i] = 1.0
        else:
            cx = np.mean(np.cos(wrap_angle(np.roll(theta, -r, axis=0) - theta)))
            cy = np.mean(np.cos(wrap_angle(np.roll(theta, -r, axis=1) - theta)))
            corr[i] = 0.5 * (cx + cy)
    return rs, corr


def strain_field(theta: np.ndarray) -> np.ndarray:
    """Local compact phase strain |D theta|^2."""
    return forward_diff(theta, 0) ** 2 + forward_diff(theta, 1) ** 2


def spectral_dimension_from_random_walk(
    theta: np.ndarray,
    n_walks: int = 2000,
    max_steps: int = 200,
    beta: float = 0.0,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Estimate spectral dimension from return probability.

    Walks occur on the periodic lattice. beta couples hopping probabilities to
    local phase strain; beta=0 is an ordinary 2D lattice random walk.
    The spectral dimension estimate is d_s(t) = -2 d log P_return / d log t.
    """
    rng = np.random.default_rng(seed)
    nx, ny = theta.shape
    returns = np.zeros(max_steps + 1, dtype=float)
    returns[0] = 1.0

    # Exact lazy-walk heat-kernel trace for the ordinary periodic 2D lattice.
    # This gives a stable baseline: d_s approaches 2 before finite-size saturation.
    if beta == 0.0:
        kx = 2.0 * np.pi * np.arange(nx) / nx
        ky = 2.0 * np.pi * np.arange(ny) / ny
        lam = 0.5 + 0.25 * (np.cos(kx)[:, None] + np.cos(ky)[None, :])
        for t in range(1, max_steps + 1):
            returns[t] = float(np.mean(lam ** t))
    else:
        strain = strain_field(theta)
        starts = np.column_stack([rng.integers(nx, size=n_walks), rng.integers(ny, size=n_walks)])
        pos = starts.copy()
        dirs = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]], dtype=int)
        for t in range(1, max_steps + 1):
            for i in range(n_walks):
                candidates = (pos[i] + dirs) % np.array([nx, ny])
                weights = np.exp(-beta * strain[candidates[:, 0], candidates[:, 1]])
                weights = weights / np.sum(weights)
                choice = rng.choice(4, p=weights)
                pos[i] = candidates[choice]
            returns[t] = np.mean(np.all(pos == starts, axis=1))

    times = np.arange(max_steps + 1)
    eps = 1e-15
    valid = times >= 2
    logt = np.log(times[valid])
    logp = np.log(np.maximum(np.abs(returns[valid]), eps))
    slope = np.gradient(logp, logt)
    ds_full = np.full_like(returns, np.nan, dtype=float)
    ds_full[valid] = -2.0 * slope
    return times, returns, ds_full
