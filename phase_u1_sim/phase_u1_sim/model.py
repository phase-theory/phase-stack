from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from .lattice import Lattice2D, forward_diff, laplacian_sin, wrap_angle


@dataclass
class U1Model:
    """Compact U(1) phase-functional model on a periodic 2D lattice.

    Energy / inconsistency functional:
        I[theta] = K sum_links (1 - cos(Delta theta))
                   + lambda_p sum_sites (1 - cos(q theta))

    The first term is the compact lattice version of |grad theta|^2.
    The optional pinning term can break continuous degeneracy and test robustness.
    """

    lattice: Lattice2D
    K: float = 1.0
    lambda_p: float = 0.0
    q: int = 1

    def energy_density(self, theta: np.ndarray) -> np.ndarray:
        ex = 1.0 - np.cos(forward_diff(theta, axis=0))
        ey = 1.0 - np.cos(forward_diff(theta, axis=1))
        ep = self.lambda_p * (1.0 - np.cos(self.q * theta))
        return self.K * (ex + ey) + ep

    def energy(self, theta: np.ndarray) -> float:
        return float(np.sum(self.energy_density(theta)))

    def gradient(self, theta: np.ndarray) -> np.ndarray:
        grad = self.K * laplacian_sin(theta)
        if self.lambda_p != 0.0:
            grad += self.lambda_p * self.q * np.sin(self.q * theta)
        return grad

    def relax(
        self,
        theta0: np.ndarray,
        steps: int = 1000,
        dt: float = 0.05,
        noise: float = 0.0,
        seed: int | None = None,
        sample_every: int = 10,
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Gradient-flow relaxation with optional Gaussian coherence noise."""
        rng = np.random.default_rng(seed)
        theta = theta0.copy()
        energies: list[float] = []
        vortex_counts: list[int] = []
        samples: list[int] = []
        from .defects import count_vortices

        for step in range(steps + 1):
            if step % sample_every == 0:
                energies.append(self.energy(theta))
                vortex_counts.append(count_vortices(theta)["total_abs"])
                samples.append(step)
            if step == steps:
                break
            eta = noise * np.sqrt(max(dt, 0.0)) * rng.normal(size=theta.shape)
            theta = wrap_angle(theta - dt * self.gradient(theta) + eta)
        history = {
            "step": np.asarray(samples, dtype=int),
            "energy": np.asarray(energies, dtype=float),
            "vortex_abs_count": np.asarray(vortex_counts, dtype=int),
        }
        return theta, history
