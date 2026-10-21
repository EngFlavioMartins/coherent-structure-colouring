"""Coherent-structure colouring.

For N tracks sampled at the same T instants, the kinematic dissimilarity of
tracks i and j is the normalised standard deviation of their separation:

    a_ij = std_t(r_ij) / mean_t(r_ij)

With the degree matrix D (d_ii = sum_k a_ik) and the graph Laplacian
L = D - A, the CSC values X are eigenvectors of the generalised problem
L X = xi D X (Eq. 1-3 of the paper). The eigenvector of the largest eigenvalue
is the classical CSC. On sparse measured tracks it mostly separates fast from
slow fluid; the trailing vortices are separated by one of the next modes.
``select_mode`` picks that mode by comparing each mode, interpolated onto a
cross-flow grid, with the streamwise vorticity estimated from the same tracks
(the field correlation used in Sect. 4 of the paper).

Only relative CSC values carry meaning; they are rescaled to [-1, 1].
"""
import numpy as np
from scipy.linalg import eigh
from scipy.spatial.distance import pdist, squareform
from scipy.stats import binned_statistic_2d


def tracks_from_table(table, n_frames=None, max_speed=None):
    """Arrange rows (x, y, z, track id, frame, u, v, w) into arrays (N, T, 3).

    With ``n_frames`` = T, only tracks with at least T samples are kept and
    each is cut to its first T samples (as in the 2020 data preparation).
    Without it, all tracks are cut to the shortest track length. Tracks with
    any velocity component of magnitude ``max_speed`` or more are left out.
    Returns positions, velocities and the ids of the kept tracks.
    """
    ids = table[:, 3].astype(int)
    unique = np.unique(ids)
    if max_speed is not None:
        bad = np.unique(ids[np.any(np.abs(table[:, 5:8]) >= max_speed, axis=1)])
        unique = np.setdiff1d(unique, bad)
    lengths = np.array([np.sum(ids == k) for k in unique])
    T = lengths.min() if n_frames is None else n_frames
    keep = unique[lengths >= T]
    pos = np.empty((len(keep), T, 3))
    vel = np.empty((len(keep), T, 3))
    for n, k in enumerate(keep):
        rows = table[ids == k]
        rows = rows[np.argsort(rows[:, 4])][:T]
        pos[n], vel[n] = rows[:, :3], rows[:, 5:8]
    return pos, vel, keep


def adjacency_matrix(tracks):
    """a_ij = std(r_ij)/mean(r_ij) over time, with a zero diagonal."""
    n, T, _ = tracks.shape
    r = np.stack([squareform(pdist(tracks[:, t])) for t in range(T)])   # (T, N, N)
    mean = r.mean(axis=0)
    std = r.std(axis=0)
    np.fill_diagonal(mean, 1.0)
    A = std / mean
    np.fill_diagonal(A, 0.0)
    return A


def _rescale(x):
    return 2 * (x - x.min()) / (x.max() - x.min()) - 1


def leading_modes(tracks, n_modes=8):
    """Eigenvalues (descending) and CSC modes (columns, each rescaled to [-1, 1])."""
    A = adjacency_matrix(tracks)
    D = np.diag(A.sum(axis=1))
    vals, vecs = eigh(D - A, D)              # generalised symmetric problem
    order = np.argsort(vals)[::-1][:n_modes]
    return vals[order], np.column_stack([_rescale(vecs[:, i]) for i in order])


def coherent_structure_colouring(tracks, mode=0):
    """CSC value per track from the given mode (0 = largest eigenvalue), in [-1, 1]."""
    return leading_modes(tracks, mode + 1)[1][:, mode]


def binned_field(points, values, y_edges, z_edges):
    """Mean of ``values`` at ``points`` (x, y, z) on a cross-flow (y, z) grid, and the sample count."""
    mean = binned_statistic_2d(points[:, 1], points[:, 2], values, "mean", bins=[y_edges, z_edges]).statistic
    count = binned_statistic_2d(points[:, 1], points[:, 2], values, "count", bins=[y_edges, z_edges]).statistic
    return mean, count


def streamwise_vorticity(positions, velocities, y_edges, z_edges):
    """omega_x = dw/dy - dv/dz from track velocities binned on a cross-flow grid."""
    pts, vel = positions.reshape(-1, 3), velocities.reshape(-1, 3)
    v, count = binned_field(pts, vel[:, 1], y_edges, z_edges)
    w, _ = binned_field(pts, vel[:, 2], y_edges, z_edges)
    wx = np.gradient(w, y_edges[1] - y_edges[0], axis=0) - np.gradient(v, z_edges[1] - z_edges[0], axis=1)
    return wx, count


def select_mode(positions, velocities, modes, y_edges, z_edges, min_count=20, reference=None):
    """Index of the mode whose cross-flow field correlates best with |omega_x|.

    Each mode is interpolated onto the (y, z) grid by bin averaging, as the
    paper does before comparing CSC with vorticity. ``reference`` is an
    optional (omega_x, count) pair on the same grid, e.g. from a denser track
    set; by default omega_x is estimated from the given tracks. Returns the
    index, the correlation of every mode, and the sign that makes the vortex
    positive.
    """
    T = positions.shape[1]
    wx, count = reference if reference is not None else streamwise_vorticity(positions, velocities, y_edges, z_edges)
    pts = positions.reshape(-1, 3)
    corr = []
    for m in modes.T:
        field, n = binned_field(pts, np.repeat(m, T), y_edges, z_edges)
        ok = (count >= min_count) & np.isfinite(wx) & (n > 0)
        corr.append(np.corrcoef(field[ok], np.abs(wx[ok]))[0, 1])
    corr = np.array(corr)
    best = int(np.argmax(np.abs(corr)))
    return best, corr, float(np.sign(corr[best]))
