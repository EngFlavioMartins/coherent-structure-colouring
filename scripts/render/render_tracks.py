"""ParaView (pvpython) render of CSC-coloured Ahmed-body tracks in the OpenONDA style.

Usage: pvpython render_tracks.py <tracks.vtp> <output png> <tube radius> [width height]

Black background, view along the stream. Tracks are tubes coloured by the
selected CSC mode with signed_dark: tracks in the trailing vortex glow red,
tracks outside it blue, and undecided tracks fade into the black. The rear
face of the body (x = -0.99 D, -1.1 <= y/D <= 0, 0 <= z/D <= 1.2, as in the
original MATLAB figures) is matte grey.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import onda_style as style  # noqa: E402
from paraview.simple import Plane, Show, Tube, XMLPolyDataReader  # noqa: E402

src, out, radius = Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3])
width, height = (int(a) for a in (sys.argv[4:6] if len(sys.argv) > 5 else (1200, 1200)))

view = style.setup_view(width, height)
C_RANGE = 1.35      # CSC spans [-1, 1]; the wider map range keeps both ends saturated, not pastel
lut = style.lut("csc", "signed_dark", -C_RANGE, C_RANGE)
tubes = Tube(Input=XMLPolyDataReader(FileName=[str(src)]))
tubes.Radius = radius
tubes.NumberofSides = 12
d = Show(tubes, view)
style.mapped(d, "csc", lut, roughness=0.3)
lut.RescaleTransferFunction(-C_RANGE, C_RANGE)

rear = Plane(Origin=[-0.99, -1.1, 0.0], Point1=[-0.99, 0.0, 0.0], Point2=[-0.99, -1.1, 1.2])
style.solid(Show(rear, view), style.GREY, roughness=0.5, opacity=0.45)

view.CameraPosition = [10.0, -0.2, 1.3]
view.CameraFocalPoint = [0.0, -0.2, 1.3]
view.CameraViewUp = [0, 0, 1]
view.CameraParallelProjection = 1
view.CameraParallelScale = 1.08
style.save(view, out, width, height)
print(out)
