from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from .defects import plaquette_winding
from .observables import strain_field


def save_field_plots(theta: np.ndarray, outdir: str | Path) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(5, 4))
    plt.imshow(theta, origin="lower")
    plt.colorbar(label="theta")
    plt.title("U(1) phase field")
    plt.tight_layout()
    plt.savefig(out / "phase_field.png", dpi=160)
    plt.close()

    plt.figure(figsize=(5, 4))
    plt.imshow(strain_field(theta), origin="lower")
    plt.colorbar(label="|D theta|^2")
    plt.title("compact phase strain")
    plt.tight_layout()
    plt.savefig(out / "strain_field.png", dpi=160)
    plt.close()

    plt.figure(figsize=(5, 4))
    plt.imshow(plaquette_winding(theta), origin="lower", vmin=-1, vmax=1)
    plt.colorbar(label="plaquette winding")
    plt.title("topological defects")
    plt.tight_layout()
    plt.savefig(out / "defects.png", dpi=160)
    plt.close()


def save_history_plots(history: dict[str, np.ndarray], outdir: str | Path) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(5, 4))
    plt.plot(history["step"], history["energy"])
    plt.xlabel("relaxation step")
    plt.ylabel("I[theta]")
    plt.title("phase-inconsistency relaxation")
    plt.tight_layout()
    plt.savefig(out / "energy_history.png", dpi=160)
    plt.close()

    plt.figure(figsize=(5, 4))
    plt.plot(history["step"], history["vortex_abs_count"])
    plt.xlabel("relaxation step")
    plt.ylabel("absolute vortex count")
    plt.title("defect count")
    plt.tight_layout()
    plt.savefig(out / "vortex_count.png", dpi=160)
    plt.close()


def save_xy_plot(x, y, xlabel: str, ylabel: str, title: str, path: str | Path) -> None:
    plt.figure(figsize=(5, 4))
    plt.plot(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
