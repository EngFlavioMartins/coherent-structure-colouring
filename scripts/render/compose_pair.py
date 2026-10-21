"""Place the sparse and dense CSC renders side by side in one 3:2 image (PNG master and WebP)."""
import sys
from pathlib import Path

from PIL import Image

left, right, stem = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
a, b = Image.open(left).convert("RGB"), Image.open(right).convert("RGB")
W, H = 2 * a.width, int(2 * a.width * 2 / 3)
img = Image.new("RGB", (W, H), "white")
y0 = (H - a.height) // 2
img.paste(a, (0, y0))
img.paste(b, (a.width, y0))
img.save(stem.with_suffix(".png"), optimize=True)
img.save(stem.with_suffix(".webp"), quality=85, method=6)
for ext in (".png", ".webp"):
    print(stem.with_suffix(ext), f"{stem.with_suffix(ext).stat().st_size / 1e3:.0f} kB")
