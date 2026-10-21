"""Place the sparse and dense CSC renders side by side and add the LaTeX overlay.

Usage: python compose_tracks.py <sparse png> <dense png> <output stem>
"""
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from overlay import compose  # noqa: E402

left, right, stem = (Path(a) for a in sys.argv[1:4])
a, b = Image.open(left).convert("RGB"), Image.open(right).convert("RGB")
side = 980
a, b = a.resize((side, side), Image.LANCZOS), b.resize((side, side), Image.LANCZOS)
canvas = Image.new("RGB", (2400, 1500))          # 16:10, room for labels above and the bar on the right
canvas.paste(a, (40, 330))
canvas.paste(b, (40 + side, 330))
raw = Path(tempfile.mkdtemp()) / "pair.png"
canvas.save(raw)
compose(raw, stem,
        bar=dict(name="signed_dark", vmin=-1, vmax=1, x=78.5, y=12, height=24, title="CSC",
                 ticks=[(0.5 - 0.5 / 1.35, "out"), (0.5 + 0.5 / 1.35, "in")]),   # CSC = -1 and 1 on the +/-1.35 map
        labels=[(19.9, 46.0, "Sparse", "center"), (56.6, 46.0, "Dense", "center")])
