from __future__ import annotations

import numpy as np
from .lattice import wrap_angle


def plaquette_winding(theta: np.ndarray) -> np.ndarray:
    """Integer U(1) winding number on each plaquette."""
    d01 = wrap_angle(np.roll(theta, -1, axis=0) - theta)
    d12 = wrap_angle(np.roll(np.roll(theta, -1, axis=0), -1, axis=1) - np.roll(theta, -1, axis=0))
    d23 = wrap_angle(np.roll(theta, -1, axis=1) - np.roll(np.roll(theta, -1, axis=0), -1, axis=1))
    d30 = wrap_angle(theta - np.roll(theta, -1, axis=1))
    winding = (d01 + d12 + d23 + d30) / (2.0 * np.pi)
    return np.rint(winding).astype(int)


def vortex_positions(theta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    w = plaquette_winding(theta)
    vortices = np.argwhere(w > 0)
    antivortices = np.argwhere(w < 0)
    return vortices, antivortices


def count_vortices(theta: np.ndarray) -> dict[str, int]:
    w = plaquette_winding(theta)
    n_plus = int(np.sum(w > 0))
    n_minus = int(np.sum(w < 0))
    return {"positive": n_plus, "negative": n_minus, "net": int(np.sum(w)), "total_abs": n_plus + n_minus}
