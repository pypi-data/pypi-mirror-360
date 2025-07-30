"""
MolMetrics: A package for calculating QED scores, molecular descriptors,
and geometry descriptors for libraries of small molecules.
"""

__version__ = "1.0.0"

from .io import make_from_smiles, make_from_sdf, make_from_pickle, save_df
from .util import parallel_apply, remove_substructure
from .qed import add_qed, add_qed_properties
from .mol_describe import add_mol_descriptors
from .geometry import add_geometry
