"""Colour near-wake Ahmed-body tracks with CSC and write them as VTK polylines.

Two seeding densities are drawn from the cleaned near-wake tracks (mean x
between 0.3 D and 2.5 D behind the rear face, T = 10 frames, tracks with any
velocity component of 16 or more left out): a sparse random subset of 400
tracks and the dense set of all of them. For each set, CSC is computed
independently, and the mode that separates the trailing (C-pillar) vortex is
chosen by comparing each mode with |omega_x| from the dense set (Sect. 4 of the
paper). The sign is set so that the vortex is positive. Each tube is exactly the
10-frame window its CSC value was computed from.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from coherent_structure_colouring import leading_modes, select_mode, streamwise_vorticity, tracks_from_table  # noqa: E402

T, X_RANGE, MAX_SPEED, N_SPARSE, SEED = 10, (0.3, 2.5), 16, 400, 0
Y_EDGES, Z_EDGES = np.linspace(-0.8, 0.8, 13), np.linspace(0.6, 2.2, 13)
OUT = ROOT / "outputs" / "render"
OUT.mkdir(parents=True, exist_ok=True)

table = loadmat(ROOT / "data" / "ahmed_body" / "CSC_large_scale_EXP18_Np1940_Nt97_results.mat", squeeze_me=True)["input"]
pos, vel, _ = tracks_from_table(table, n_frames=T, max_speed=MAX_SPEED)
x_mean = pos[:, :, 0].mean(axis=1)
near = (x_mean > X_RANGE[0]) & (x_mean < X_RANGE[1])
pos, vel = pos[near], vel[near]
reference = streamwise_vorticity(pos, vel, Y_EDGES, Z_EDGES)

sets = {"sparse": np.random.default_rng(SEED).choice(len(pos), N_SPARSE, replace=False),
        "dense": np.arange(len(pos))}
summary = {}
for name, pick in sets.items():
    _, modes = leading_modes(pos[pick], 8)
    best, corr, sign = select_mode(pos[pick], vel[pick], modes, Y_EDGES, Z_EDGES, reference=reference)
    csc = sign * modes[:, best]
    lo, hi = np.percentile(csc, [2, 98])
    colour = np.clip(2 * (csc - lo) / (hi - lo) - 1, -1, 1)
    points = pos[pick].reshape(-1, 3)
    lines = np.hstack([[T, *range(i * T, (i + 1) * T)] for i in range(len(pick))])
    poly = pv.PolyData(points, lines=lines)
    poly["csc"] = np.repeat(colour, T)
    poly.save(OUT / f"tracks_{name}.vtp")
    summary[name] = {"tracks": int(len(pick)), "mode": best, "r_abs_omega_x": round(float(corr[best] * sign), 2)}
    print(f"{name}: {len(pick)} tracks, mode {best}, r(|omega_x|) = {corr[best] * sign:+.2f}")
(OUT / "csc_summary.json").write_text(json.dumps(summary, indent=1))
