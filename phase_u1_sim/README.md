# phase-u1-sim

A working U(1) simulation package for the first deployable Phase Theory paper:
**A Minimal Phase-Functional Program for Emergent Spacetime and Topological Matter**.

This repository implements the first testable sector only: a compact U(1) phase field on a finite lattice. It does **not** claim to prove the full unification program. It is designed to make the proposal operational by producing reproducible numerical objects: energy relaxation, topological defect counts, phase correlations, spectral-dimension estimates, and linearized dispersion curves.

## Model

The simulated phase field is

```text
theta_i in (-pi, pi]
```

on a periodic 2D square lattice. The minimal phase-inconsistency functional is

```text
I[theta] = K sum_<ij> [1 - cos(theta_j - theta_i)]
         + lambda_p sum_i [1 - cos(q theta_i)]
```

where angular differences are compactly wrapped. The first term is the lattice U(1) analogue of phase-gradient inconsistency. The optional pinning term is included for robustness tests.

Relaxation uses the update rule

```text
theta <- wrap(theta - dt * delta I / delta theta + noise * sqrt(dt) * eta)
```

This is the U(1) lattice analogue of constrained phase relaxation from the broader Phase Theory manuscript.

## What the package measures

1. **Defect stability and annihilation**
   - plaquette winding number
   - vortex / antivortex counts
   - net topological charge

2. **Inconsistency relaxation**
   - energy history `I[theta]`
   - vortex count history

3. **Correlation structure**
   - radial phase correlation `C(r)=<cos(theta(x+r)-theta(x))>`

4. **Spectral dimension proxy**
   - random-walk return probability
   - `d_s(t) = -2 d log P_return / d log t`

5. **Linearized propagating-mode dispersion**
   - 1D small-amplitude wave equation
   - measured frequency versus lattice and continuum expectation

## Install

From the repository root:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

or without editable install:

```bash
pip install -r requirements.txt
```

## Run examples

### 1. Vortex-antivortex relaxation

```bash
python -m phase_u1_sim.cli relax --config examples/vortex_pair.yaml
```

Outputs appear in `results/vortex_pair/`:

- `phase_field.png`
- `strain_field.png`
- `defects.png`
- `energy_history.png`
- `vortex_count.png`
- `correlation.png`
- `theta_final.npy`
- `history.npz`
- `summary.json`

### 2. Random quench

```bash
python -m phase_u1_sim.cli relax --config examples/random_quench.yaml
```

### 3. Spectral dimension from a saved field

```bash
python -m phase_u1_sim.cli spectral \
  --theta results/vortex_pair/theta_final.npy \
  --outdir results/spectral \
  --walks 2000 \
  --steps 200
```

### 4. Linearized dispersion

```bash
python -m phase_u1_sim.cli dispersion --outdir results/dispersion --mode-k 4
```

## Run tests

```bash
pytest -q
```

## Interpretation discipline

This package is intentionally narrow. It supports the first paper only if it passes the following gates:

- relaxation lowers the compact inconsistency functional in low-noise runs;
- plaquette winding detects integer topological charge;
- vortex-antivortex configurations show neutral net charge and possible annihilation;
- correlations and spectral-dimension estimates are reproducible under finite-size scaling;
- linearized modes recover the expected low-k dispersion.

Failure on any of these gates does not falsify all Phase Theory. It falsifies this minimal U(1) implementation or its parameter choices.

## Suggested next upgrades

- finite-size scaling suite over `N = 32, 64, 128, 256`;
- automated vortex trajectory tracking;
- Metropolis / Langevin sampler for finite-temperature phase ensembles;
- 3D lattice extension where vortex lines replace point vortices;
- SU(2) prototype with compact group-valued fields;
- comparison to XY-model and lattice gauge theory baselines.
