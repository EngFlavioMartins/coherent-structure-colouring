"""Place the sparse and dense CSC renders side by side and add the LaTeX overlay.

Usage: python compose_tracks.py <sparse png> <dense png> <output stem>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from overlay import compose  # noqa: E402

C_RANGE = 1.35          # same as render_tracks.py: CSC = -1 and 1 sit inside the map
left, right, stem = (Path(a) for a in sys.argv[1:4])
compose([(left, "Sparse"), (right, "Dense")], stem, layout="row",
        bar=dict(name="signed_dark", vmin=-1, vmax=1, title="CSC",
                 ticks=[(0.5 - 0.5 / C_RANGE, "out"), (0.5 + 0.5 / C_RANGE, "in")]))
