# Coherent-structure colouring

<p align="center">
  <a href="https://doi.org/10.1007/s00348-021-03135-5"><img src="https://img.shields.io/badge/paper-10.1007%2Fs00348--021--03135--5-1F6FEB" alt="paper: 10.1007/s00348-021-03135-5"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white" alt="python: 3.10+"></a>
  <a href="https://github.com/EngFlavioMartins/coherent-structure-colouring/blob/HEAD/LICENSE"><img src="https://img.shields.io/badge/license-MIT-2E7D32" alt="license: MIT"></a>
  <a href="https://engflaviomartins.github.io/#work-csc"><img src="https://img.shields.io/badge/website-research%20page-15212B" alt="website: research page"></a>
</p>

**Find vortices in sparse particle tracks.**

<p align="center"><img src="docs/assets/render.webp" width="560" alt="Particle tracks measured behind an Ahmed body, seen along the stream, for sparse and dense seeding; tracks in the trailing vortex glow red"></p>

Coherent-structure colouring (CSC) gives each particle track a value from how its distance to every other track changes in time; tracks that move together get similar values. This Python version also picks the eigenvector that separates the vortex (`select_mode`), because on sparse measured tracks the classical leading eigenvector mostly separates fast from slow fluid. The repository includes Ahmed-body tracks from the paper's experiment.

## Get started

```bash
git clone https://github.com/EngFlavioMartins/coherent-structure-colouring.git
cd coherent-structure-colouring
pip install -r requirements.txt
python examples/ahmed_body.py
```

This prints, for each leading mode, how it relates to speed and to vorticity, and marks the one selected. The 2020 MATLAB code is not available, and this version does not reproduce the CSC values stored with the data.

## Make the figure above

```bash
sh scripts/render/make_figure.sh
```

You need [ParaView](https://www.paraview.org/download/) (for `pvpython`), a LaTeX installation, and `pip install pyvista pillow`.

## Cite

This code implements the method of the paper below. If you use it, please cite:

```bibtex
@article{martins2021csc,
  author  = {Martins, Flavio A. C. and Sciacchitano, A. and Rival, D. E.},
  title   = {Detection of Vortical Structures in Sparse Lagrangian Data Using Coherent-Structure Colouring},
  journal = {Experiments in Fluids},
  volume  = {62},
  number  = {4},
  pages   = {69},
  year    = {2021},
  doi     = {10.1007/s00348-021-03135-5}
}
```

GitHub's **Cite this repository** button (from [CITATION.cff](CITATION.cff)) gives the same reference in other formats.

## Licence

MIT; see [LICENSE](LICENSE).
