#!/usr/bin/env bash
set -euo pipefail
python -m phase_u1_sim.cli relax --config examples/random_quench.yaml --outdir results/random_quench_demo
python -m phase_u1_sim.cli spectral --theta results/random_quench_demo/theta_final.npy --outdir results/spectral_demo --walks 2000 --steps 200
python -m phase_u1_sim.cli dispersion --outdir results/dispersion_demo --mode-k 4
pytest -q
