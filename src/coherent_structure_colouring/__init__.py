"""Coherent-structure colouring (CSC) of sparse Lagrangian tracks.

Python implementation of the method used in Martins, Sciacchitano & Rival
(2021), Exp. Fluids 62, 69, doi:10.1007/s00348-021-03135-5, after
Schlueter-Kuck & Dabiri (2017).
"""
from .csc import (adjacency_matrix, coherent_structure_colouring, leading_modes, select_mode,
                  streamwise_vorticity, tracks_from_table)

__all__ = ["adjacency_matrix", "coherent_structure_colouring", "leading_modes", "select_mode",
           "streamwise_vorticity", "tracks_from_table"]
