import numpy as np
from phase_u1_sim.lattice import Lattice2D
from phase_u1_sim.model import U1Model
from phase_u1_sim.defects import count_vortices
from phase_u1_sim.dispersion import simulate_linear_wave


def test_energy_decreases_for_smooth_field():
    lat = Lattice2D(16, 16)
    model = U1Model(lat, K=1.0)
    theta0 = lat.random_phase(seed=1)
    _, hist = model.relax(theta0, steps=20, dt=0.02, noise=0.0, sample_every=1)
    assert hist["energy"][-1] <= hist["energy"][0]


def test_random_periodic_field_has_zero_net_charge():
    lat = Lattice2D(48, 48)
    theta = lat.random_phase(seed=2)
    counts = count_vortices(theta)
    assert counts["net"] == 0
    assert counts["total_abs"] > 0


def test_dispersion_returns_positive_frequency():
    res = simulate_linear_wave(nx=64, steps=200, dt=0.1, mode_k=3)
    assert res["omega_measured"] > 0
    assert res["omega_lattice_expected"] > 0
