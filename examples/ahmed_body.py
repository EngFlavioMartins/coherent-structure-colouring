"""Coherent-structure colouring of PTV tracks in the wake of an Ahmed body.

Computes the leading CSC modes of the near-wake tracks (T = 10 frames,
1 rear-face distance D behind the body and beyond) and reports, for each mode,
the correlation of its cross-flow field with the track speed and with the
streamwise vorticity |omega_x|. The mode chosen by ``select_mode`` is the one
that separates the trailing (C-pillar) vortex.
"""
import sys
from pathlib import Path

import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from coherent_structure_colouring import leading_modes, select_mode, tracks_from_table  # noqa: E402
from coherent_structure_colouring.csc import binned_field  # noqa: E402

T, X_RANGE = 10, (0.3, 2.5)
Y_EDGES, Z_EDGES = np.linspace(-0.8, 0.8, 13), np.linspace(0.6, 2.2, 13)

table = loadmat(ROOT / "data" / "ahmed_body" / "CSC_large_scale_EXP18_Np1940_Nt97_results.mat", squeeze_me=True)["input"]
pos, vel, ids = tracks_from_table(table, n_frames=T, max_speed=16)
x_mean = pos[:, :, 0].mean(axis=1)
sel = (x_mean > X_RANGE[0]) & (x_mean < X_RANGE[1])
pos, vel = pos[sel], vel[sel]
vals, modes = leading_modes(pos, 8)
best, corr, sign = select_mode(pos, vel, modes, Y_EDGES, Z_EDGES)
speed, count = binned_field(pos.reshape(-1, 3), np.linalg.norm(vel, axis=2).ravel(), Y_EDGES, Z_EDGES)
ok = count >= 20
print(f"{len(pos)} near-wake tracks, T = {T}")
for i, m in enumerate(modes.T):
    f, _ = binned_field(pos.reshape(-1, 3), np.repeat(m, T), Y_EDGES, Z_EDGES)
    print(f"mode {i}: xi = {vals[i]:.3f}  r(speed) = {np.corrcoef(f[ok], speed[ok])[0, 1]:+.2f}  r(|omega_x|) = {corr[i]:+.2f}"
          + ("   <- selected" if i == best else ""))
