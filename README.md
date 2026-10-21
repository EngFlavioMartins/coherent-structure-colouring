# Coherent-structure colouring

**Coherent-structure colouring of sparse particle tracks.**

![Particle tracks measured behind an Ahmed body, seen along the stream, for sparse and dense seeding; tracks in the trailing vortex are coloured red](docs/assets/render.webp)

Coherent-structure colouring (CSC) of sparse Lagrangian particle tracks, in Python. It accompanies

> F. A. C. Martins, A. Sciacchitano and D. E. Rival (2021). Detection of vortical structures in sparse Lagrangian data using coherent-structure colouring. *Experiments in Fluids* 62, 69. [doi:10.1007/s00348-021-03135-5](https://doi.org/10.1007/s00348-021-03135-5)

The method follows Schlueter-Kuck & Dabiri (2017). For N tracks sampled at the same T instants, the kinematic dissimilarity of tracks *i* and *j* is a<sub>ij</sub> = σ(r<sub>ij</sub>)/⟨r<sub>ij</sub>⟩, the normalised standard deviation of their separation. With degree matrix D and graph Laplacian L = D − A, the CSC values are eigenvectors of L X = ξ D X (Eqs. 1–3 of the paper). Only relative CSC values carry meaning; they are rescaled to [−1, 1].

### Choosing the mode

On sparse measured tracks, the eigenvector of the largest eigenvalue mostly separates fast fluid from slow fluid. In the Ahmed-body data, its cross-flow field correlates with track speed at r ≈ 0.7. The trailing (C-pillar) vortex is separated by a later mode. `select_mode` picks it as follows. Each of the leading modes is interpolated onto a cross-flow grid by bin averaging, and compared with the streamwise vorticity |ω<sub>x</sub>| estimated from track velocities on the same grid. This is the field comparison of Sect. 4 of the paper. The reference field can come from a denser track set, as the paper's reference fields did.

## Quick start

```bash
pip install numpy scipy
python examples/ahmed_body.py
```

```python
from coherent_structure_colouring import leading_modes, select_mode, tracks_from_table
pos, vel, ids = tracks_from_table(table, n_frames=10, max_speed=16)    # arrays (N, T, 3)
xi, modes = leading_modes(pos, 8)
best, corr, sign = select_mode(pos, vel, modes, y_edges, z_edges)
csc = sign * modes[:, best]
```

`examples/ahmed_body.py` prints, for each leading mode of the near-wake tracks, its correlation with speed and with |ω<sub>x</sub>|. Mode 0 follows speed (r = +0.70); mode 1 follows the trailing vortex (r = +0.39) and is selected.

## Data

`data/ahmed_body/` holds three subsets of the time-resolved Shake-the-Box tracks measured behind the 1:2 Ahmed body (Exp. Fluids 2021, Sect. 3). Each subset was prepared in 2020 with a different minimum track length; together they hold 158, 1337 and 1940 tracks. Each `.mat` file holds `input`, with rows (x, y, z, track id, frame, u, v, w) in units of D, and `solution`, the CSC values computed in 2020. The rear face of the body lies at x = −0.99 D.

The 2020 MATLAB implementation is not available. This Python version follows the paper's equations, but it does not reproduce the stored 2020 `solution` values: the correlation with them is at most 0.27. The stored values follow streamwise position (Spearman ≈ 0.5). Tracks with any velocity component of 16 or more are left out, as in the 2022 post-processing.

## Repository guide

| Location | Purpose |
| --- | --- |
| `src/coherent_structure_colouring/` | CSC algorithm and track utilities |
| `examples/ahmed_body.py` | CSC of the Ahmed-body tracks |
| `data/ahmed_body/` | Track subsets from the 2020 analysis |
| `scripts/render/` | Scripts that make the website images (ParaView `pvpython`, pyvista, cmcrameri, Pillow) |

To reproduce the website images:

```bash
python scripts/render/compute_tracks.py
pvpython scripts/render/render_tracks.py outputs/render/tracks_sparse.vtp outputs/render/panel_sparse.png 0.008 1200 1200
pvpython scripts/render/render_tracks.py outputs/render/tracks_dense.vtp outputs/render/panel_dense.png 0.008 1200 1200
python scripts/render/compose_pair.py outputs/render/panel_sparse.png outputs/render/panel_dense.png outputs/render/coherent-structure-colouring
```

The image shows near-wake tracks seen along the stream. On the left is a sparse set of 400 tracks, and on the right all 1197. CSC is computed separately for each set, and the vortex mode is selected against |ω<sub>x</sub>| from the dense set. Colour is the selected mode (Crameri `vik`): tracks in the trailing vortex are red. The grey panel is the rear face of the body.

## Citing

This code implements the method of F. A. C. Martins, A. Sciacchitano and D. E. Rival (2021), Detection of vortical structures in sparse Lagrangian data using coherent-structure colouring, *Experiments in Fluids* 62, 69, [doi:10.1007/s00348-021-03135-5](https://doi.org/10.1007/s00348-021-03135-5).

GitHub's *Cite this repository* button uses [CITATION.cff](CITATION.cff).

## Licence

MIT; see [LICENSE](LICENSE).
