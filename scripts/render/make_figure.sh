#!/bin/sh
# Make the website figure in outputs/render/ (PNG, WebP and PDF).
# Needs Python with the packages in the README, ParaView's pvpython and LaTeX.
# Set PVPYTHON if pvpython is not on your PATH, e.g.
#   PVPYTHON=/Applications/ParaView-6.1.0.app/Contents/bin/pvpython sh scripts/render/make_figure.sh
set -e
cd "$(dirname "$0")/../.."
PV=${PVPYTHON:-pvpython}
R=scripts/render
O=outputs/render
mkdir -p $O
python $R/compute_tracks.py
$PV $R/render_tracks.py $O/tracks_sparse.vtp $O/sparse-raw.png 0.008
$PV $R/render_tracks.py $O/tracks_dense.vtp $O/dense-raw.png 0.008
python $R/compose_tracks.py $O/sparse-raw.png $O/dense-raw.png $O/coherent-structure-colouring
