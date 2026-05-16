from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

from .config import load_config
from .lattice import Lattice2D
from .model import U1Model
from .defects import count_vortices
from .observables import phase_correlation, spectral_dimension_from_random_walk
from .dispersion import simulate_linear_wave
from .plotting import save_field_plots, save_history_plots, save_xy_plot


def run_relax(args: argparse.Namespace) -> None:
    cfg = load_config(args.config) if args.config else {}
    lat_cfg = cfg.get("lattice", {})
    model_cfg = cfg.get("model", {})
    run_cfg = cfg.get("relaxation", {})
    outdir = Path(args.outdir or cfg.get("outdir", "results/relax"))
    outdir.mkdir(parents=True, exist_ok=True)

    lattice = Lattice2D(nx=int(lat_cfg.get("nx", args.nx)), ny=int(lat_cfg.get("ny", args.ny)))
    model = U1Model(
        lattice=lattice,
        K=float(model_cfg.get("K", args.K)),
        lambda_p=float(model_cfg.get("lambda_p", args.lambda_p)),
        q=int(model_cfg.get("q", args.q)),
    )
    seed = int(run_cfg.get("seed", args.seed)) if run_cfg.get("seed", args.seed) is not None else None
    init = run_cfg.get("init", args.init)
    if init == "vortex_pair":
        theta0 = lattice.vortex_pair(separation=run_cfg.get("separation", None))
    elif init == "smooth":
        theta0 = lattice.smooth_phase(seed=seed)
    else:
        theta0 = lattice.random_phase(seed=seed)

    theta, history = model.relax(
        theta0,
        steps=int(run_cfg.get("steps", args.steps)),
        dt=float(run_cfg.get("dt", args.dt)),
        noise=float(run_cfg.get("noise", args.noise)),
        seed=seed,
        sample_every=int(run_cfg.get("sample_every", args.sample_every)),
    )

    np.save(outdir / "theta_final.npy", theta)
    np.savez(outdir / "history.npz", **history)
    save_field_plots(theta, outdir)
    save_history_plots(history, outdir)

    rs, corr = phase_correlation(theta)
    np.savez(outdir / "correlation.npz", r=rs, C=corr)
    save_xy_plot(rs, corr, "r", "C(r)", "phase correlation", outdir / "correlation.png")

    summary = {
        "energy_initial": float(history["energy"][0]),
        "energy_final": float(history["energy"][-1]),
        "vortices_final": count_vortices(theta),
        "outputs": [p.name for p in sorted(outdir.iterdir())],
    }
    with open(outdir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


def run_spectral(args: argparse.Namespace) -> None:
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    theta = np.load(args.theta)
    times, returns, ds = spectral_dimension_from_random_walk(
        theta,
        n_walks=args.walks,
        max_steps=args.steps,
        beta=args.beta,
        seed=args.seed,
    )
    np.savez(outdir / "spectral_dimension.npz", time=times, return_probability=returns, ds=ds)
    save_xy_plot(times[1:], returns[1:], "walk step", "P(return)", "return probability", outdir / "return_probability.png")
    save_xy_plot(times[2:], ds[2:], "walk step", "d_s", "spectral dimension estimate", outdir / "spectral_dimension.png")
    print(json.dumps({"ds_median_late": float(np.nanmedian(ds[max(3, args.steps // 4):]))}, indent=2))


def run_dispersion(args: argparse.Namespace) -> None:
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    result = simulate_linear_wave(nx=args.nx, steps=args.steps, dt=args.dt, c=args.c, mode_k=args.mode_k)
    np.savez(outdir / "dispersion.npz", **result)
    save_xy_plot(result["time"], result["signal"], "time", "phi(0,t)", "linear mode signal", outdir / "mode_signal.png")
    save_xy_plot(result["freqs"], result["spectrum"], "frequency", "amplitude", "mode spectrum", outdir / "mode_spectrum.png")
    summary = {k: float(result[k]) for k in ["k", "omega_measured", "omega_lattice_expected", "omega_continuum_expected"]}
    with open(outdir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="U(1) phase-functional simulation package")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("relax", help="run compact U(1) relaxation dynamics")
    p.add_argument("--config")
    p.add_argument("--outdir", default=None)
    p.add_argument("--nx", type=int, default=64)
    p.add_argument("--ny", type=int, default=64)
    p.add_argument("--K", type=float, default=1.0)
    p.add_argument("--lambda-p", type=float, default=0.0)
    p.add_argument("--q", type=int, default=1)
    p.add_argument("--init", choices=["random", "smooth", "vortex_pair"], default="random")
    p.add_argument("--steps", type=int, default=1000)
    p.add_argument("--dt", type=float, default=0.05)
    p.add_argument("--noise", type=float, default=0.0)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--sample-every", type=int, default=10)
    p.set_defaults(func=run_relax)

    p = sub.add_parser("spectral", help="estimate spectral dimension from a saved theta field")
    p.add_argument("--theta", required=True)
    p.add_argument("--outdir", default="results/spectral")
    p.add_argument("--walks", type=int, default=2000)
    p.add_argument("--steps", type=int, default=200)
    p.add_argument("--beta", type=float, default=0.0)
    p.add_argument("--seed", type=int, default=11)
    p.set_defaults(func=run_spectral)

    p = sub.add_parser("dispersion", help="measure linearized U(1) propagating-mode dispersion")
    p.add_argument("--outdir", default="results/dispersion")
    p.add_argument("--nx", type=int, default=128)
    p.add_argument("--steps", type=int, default=600)
    p.add_argument("--dt", type=float, default=0.1)
    p.add_argument("--c", type=float, default=1.0)
    p.add_argument("--mode-k", type=int, default=4)
    p.set_defaults(func=run_dispersion)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
