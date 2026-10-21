"""ParaView (pvpython) render of CSC-coloured Ahmed-body tracks as tubes.

Usage: pvpython render_tracks.py <tracks.vtp> <output png> <tube radius> [width height]
The grey panel is the rear face of the body, placed as in the original
MATLAB figures (draw_truck.m): x = -0.99 D, -1.1 <= y/D <= 0, 0 <= z/D <= 1.2.
Colour: the selected CSC mode with Crameri's "vik" (trailing vortex red).
"""
import json
import sys
from pathlib import Path

from paraview.simple import (ColorBy, GetActiveViewOrCreate, GetColorTransferFunction, Plane,
                             SaveScreenshot, Show, Tube, XMLPolyDataReader)

src, out, radius = Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3])
width, height = (int(a) for a in (sys.argv[4:6] if len(sys.argv) > 5 else (2400, 1600)))
HERE = Path(__file__).resolve().parent

view = GetActiveViewOrCreate("RenderView")
view.ViewSize = [width, height]
view.OrientationAxesVisibility = 0
view.UseColorPaletteForBackground = 0
view.Background = [1, 1, 1]
view.EnableRayTracing = 1
view.BackEnd = "OSPRay raycaster"
view.SamplesPerPixel = 32
view.AmbientSamples = 8

tubes = Tube(Input=XMLPolyDataReader(FileName=[str(src)]))
tubes.Radius = radius
tubes.NumberofSides = 12
d = Show(tubes, view)
ColorBy(d, ("POINTS", "csc"))
lut = GetColorTransferFunction("csc")
lut.RGBPoints = json.loads((HERE / "vik.json").read_text())["vik"]
lut.ColorSpace = "RGB"
lut.AutomaticRescaleRangeMode = "Never"
d.SetScalarBarVisibility(view, False)
d.Specular, d.SpecularPower = 0.3, 30
lut.RescaleTransferFunction(-1.0, 1.0)

rear = Plane(Origin=[-0.99, -1.1, 0.0], Point1=[-0.99, 0.0, 0.0], Point2=[-0.99, -1.1, 1.2])
d = Show(rear, view)
d.ColorArrayName = ["POINTS", ""]
d.AmbientColor = d.DiffuseColor = [0.6, 0.62, 0.65]
d.Opacity = 0.85

view.CameraPosition = [10.0, -0.2, 1.3]
view.CameraFocalPoint = [0.0, -0.2, 1.3]
view.CameraViewUp = [0, 0, 1]
view.CameraParallelProjection = 1
view.CameraParallelScale = 1.08
SaveScreenshot(str(out), view, ImageResolution=[width, height], TransparentBackground=0)
print(out)
