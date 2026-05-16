from __future__ import annotations

from dataclasses import dataclass
import numpy as np

TWOPI = 2.0 * np.pi


def wrap_angle(x: np.ndarray | float) -> np.ndarray | float:
    """Map angles to (-pi, pi]."""
    return (x + np.pi) % TWOPI - np.pi


@dataclass(frozen=True)
class Lattice2D:
    """Periodic square lattice for a compact U(1) phase field."""

    nx: int
    ny: int
    dx: float = 1.0

    def shape(self) -> tuple[int, int]:
        return (self.nx, self.ny)

    def random_phase(self, seed: int | None = None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.uniform(-np.pi, np.pi, size=self.shape())

    def smooth_phase(self, seed: int | None = None, noise: float = 0.05) -> np.ndarray:
        rng = np.random.default_rng(seed)
        base = rng.uniform(-np.pi, np.pi)
        return wrap_angle(base + noise * rng.normal(size=self.shape()))

    def vortex_pair(self, separation: int | None = None) -> np.ndarray:
        """Construct an approximate vortex-antivortex phase field."""
        nx, ny = self.shape()
        if separation is None:
            separation = nx // 3
        x = np.arange(nx)[:, None]
        y = np.arange(ny)[None, :]
        cx1, cy1 = nx // 2 - separation // 2, ny // 2
        cx2, cy2 = nx // 2 + separation // 2, ny // 2
        theta1 = np.arctan2(y - cy1, x - cx1)
        theta2 = np.arctan2(y - cy2, x - cx2)
        return wrap_angle(theta1 - theta2)


def forward_diff(theta: np.ndarray, axis: int) -> np.ndarray:
    return wrap_angle(np.roll(theta, -1, axis=axis) - theta)


def laplacian_sin(theta: np.ndarray) -> np.ndarray:
    """Gradient of nearest-neighbor XY energy with compact differences."""
    grad = np.zeros_like(theta)
    for axis in (0, 1):
        d_forward = wrap_angle(np.roll(theta, -1, axis=axis) - theta)
        d_backward = wrap_angle(theta - np.roll(theta, 1, axis=axis))
        grad += np.sin(d_backward) - np.sin(d_forward)
    return grad
