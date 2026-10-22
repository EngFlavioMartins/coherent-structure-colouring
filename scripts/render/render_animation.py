"""ParaView (pvpython) animation frames: CSC-coloured tracers running along their wake tracks.

Usage: pvpython render_animation.py <tracks.vtp> <frame directory> [frames]
Same view and colours as the still figure (looking upstream along the wake axis; signed_dark:
trailing vortex red, outside it blue, undecided tracks fading into the black; matte grey rear
face of the body). The full tracks stay as thin tubes; each tracer runs along its own 10-frame track as a short comet, with its own
phase, so the red tracers circle the vortex while the rest drift; the loop is seamless.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import onda_style as style  # noqa: E402
from paraview import servermanager as sm  # noqa: E402
from paraview.simple import Plane, Show, TrivialProducer, Tube, XMLPolyDataReader  # noqa: E402
from vtkmodules.numpy_interface import dataset_adapter as dsa  # noqa: E402
from vtkmodules.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray  # noqa: E402
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData  # noqa: E402
from vtkmodules.vtkCommonCore import vtkPoints  # noqa: E402

src, out = Path(sys.argv[1]), Path(sys.argv[2])
frames = int(sys.argv[3]) if len(sys.argv) > 3 else 90
width, height = 1400, 1400
T, TAIL, SUB = 10, 3.0, 4            # samples per track, comet length (samples), sub-steps per sample

reader = XMLPolyDataReader(FileName=[str(src)])
reader.UpdatePipeline()
data = dsa.WrapDataObject(sm.Fetch(reader))
xyz = np.asarray(data.Points).reshape(-1, T, 3)            # (tracks, T, 3); every polyline has T points
csc = np.asarray(data.PointData["csc"]).reshape(-1, T)[:, 0]
n = len(xyz)
phase = np.random.default_rng(1).random(n)


def along(u):
    """Points at fractional sample u (per track) by Catmull-Rom interpolation."""
    i = np.clip(np.floor(u).astype(int), 0, T - 2)
    f = (u - i)[:, None]
    k = np.arange(n)
    p0, p1 = xyz[k, np.maximum(i - 1, 0)], xyz[k, i]
    p2, p3 = xyz[k, i + 1], xyz[k, np.minimum(i + 2, T - 1)]
    return 0.5 * (2 * p1 + (p2 - p0) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f ** 2
                  + (3 * p1 - p0 - 3 * p2 + p3) * f ** 3)


def comets(t):
    """Comet polylines at loop time t in [0, 1): each head moves over [0, T - 1 + TAIL]."""
    head = ((t + phase) % 1.0) * (T - 1 + TAIL)
    m = int(TAIL * SUB) + 1
    u = head[:, None] - np.linspace(TAIL, 0, m)[None, :]        # tail -> head
    u = np.clip(u, 0, T - 1)
    pts = np.stack([along(u[:, j]) for j in range(m)], axis=1)   # (n, m, 3)
    # taper: radius grows from the tail to the head; clipped tails collapse to a point
    radius = np.tile(np.linspace(0.003, 0.012, m), (n, 1))
    pd = vtkPolyData()
    p = vtkPoints()
    p.SetData(numpy_to_vtk(pts.reshape(-1, 3), deep=True))
    pd.SetPoints(p)
    conn = np.hstack([np.full((n, 1), m), np.arange(n * m).reshape(n, m)]).ravel()
    cells = vtkCellArray()
    cells.SetCells(n, numpy_to_vtkIdTypeArray(conn.astype(np.int64), deep=True))
    pd.SetLines(cells)
    for name, values in (("csc", np.repeat(csc, m)), ("radius", radius.ravel())):
        a = numpy_to_vtk(np.ascontiguousarray(values, dtype=float), deep=True)
        a.SetName(name)
        pd.GetPointData().AddArray(a)
    pd.GetPointData().SetActiveScalars("radius")
    return pd


view = style.setup_view(width, height)
C_RANGE = 1.35
lut = style.lut("csc", "signed_dark", -C_RANGE, C_RANGE)
producer = TrivialProducer()
producer.GetClientSideObject().SetOutput(comets(0.0))
tubes = Tube(Input=producer)
tubes.Scalars = ["POINTS", "radius"]
tubes.VaryRadius = "By Absolute Scalar"
tubes.Radius = 1.0
tubes.NumberofSides = 12
tubes.Capping = 1
style.mapped(Show(tubes, view), "csc", lut, roughness=0.3)
lut.RescaleTransferFunction(-C_RANGE, C_RANGE)
thin = Tube(Input=reader)
thin.Radius = 0.0035
thin.NumberofSides = 10
style.mapped(Show(thin, view), "csc", lut, roughness=0.3)
rear = Plane(Origin=[-0.99, -1.1, 0.0], Point1=[-0.99, 0.0, 0.0], Point2=[-0.99, -1.1, 1.2])
style.solid(Show(rear, view), style.GREY, roughness=0.5, opacity=0.45)

view.CameraPosition = [10.0, -0.2, 1.3]
view.CameraFocalPoint = [0.0, -0.2, 1.3]
view.CameraViewUp = [0, 0, 1]
view.CameraParallelProjection = 1
view.CameraParallelScale = 1.08
out.mkdir(parents=True, exist_ok=True)
for k in range(frames):
    producer.GetClientSideObject().SetOutput(comets(k / frames))
    producer.MarkModified(producer)
    style.save(view, out / f"frame_{k:03d}.png", width, height)
    print(k, end=" ", flush=True)
print()
