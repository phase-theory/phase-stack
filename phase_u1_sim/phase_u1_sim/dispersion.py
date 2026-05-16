from __future__ import annotations

import numpy as np


def simulate_linear_wave(
    nx: int = 128,
    steps: int = 600,
    dt: float = 0.1,
    c: float = 1.0,
    mode_k: int = 4,
    amplitude: float = 1e-3,
) -> dict[str, np.ndarray | float]:
    """Measure dispersion of a small U(1) phase perturbation.

    Evolves phi_tt = c^2 Laplacian(phi) on a periodic 1D ring. This is the
    linearized propagating-mode limit of the compact phase model.
    """
    x = np.arange(nx)
    k_phys = 2.0 * np.pi * mode_k / nx
    phi = amplitude * np.sin(k_phys * x)
    v = np.zeros_like(phi)
    series = np.zeros(steps)
    lap = lambda a: np.roll(a, -1) - 2.0 * a + np.roll(a, 1)
    for t in range(steps):
        series[t] = phi[0]
        v += dt * c * c * lap(phi)
        phi += dt * v
    freqs = np.fft.rfftfreq(steps, d=dt)
    spectrum = np.abs(np.fft.rfft(series - np.mean(series)))
    peak_idx = int(np.argmax(spectrum[1:]) + 1) if spectrum.size > 1 else 0
    omega_measured = 2.0 * np.pi * freqs[peak_idx]
    omega_lattice = 2.0 * c * abs(np.sin(k_phys / 2.0))
    omega_continuum = c * abs(k_phys)
    return {
        "time": np.arange(steps) * dt,
        "signal": series,
        "freqs": freqs,
        "spectrum": spectrum,
        "k": k_phys,
        "omega_measured": float(omega_measured),
        "omega_lattice_expected": float(omega_lattice),
        "omega_continuum_expected": float(omega_continuum),
    }
