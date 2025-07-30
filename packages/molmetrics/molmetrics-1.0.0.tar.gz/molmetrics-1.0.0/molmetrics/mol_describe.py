#!/usr/bin/env python3
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem import Crippen
from .util import parallel_apply
import logging

def calc_mol_descriptors(mol: Chem.Mol) -> dict | None:
    """
    Calculate selected molecular descriptors for a molecule.

    Args:
        mol (Chem.Mol): RDKit molecule object.

    Returns:
        dict | None: Dictionary of molecular descriptors or None if an error occurs.
    """
    try:
        return {
            "Num Ring": rdMolDescriptors.CalcNumRings(mol),
            "Num Ar Ring": rdMolDescriptors.CalcNumAromaticRings(mol),
            "Num ArHetcy": rdMolDescriptors.CalcNumAromaticHeterocycles(mol),
            "Num Hetcy": rdMolDescriptors.CalcNumHeterocycles(mol),
            "Num Hetatm": rdMolDescriptors.CalcNumHeteroatoms(mol),
            "Num Spiro": rdMolDescriptors.CalcNumSpiroAtoms(mol),
            "Frac Sp3": rdMolDescriptors.CalcFractionCSP3(mol),
            "MR": Crippen.MolMR(mol),
        }
    except Exception as e:
        logging.error(f"Error calculating molecular descriptors: {e}", exc_info=True)
        return None


def add_mol_descriptors(df: pd.DataFrame, molcol: str) -> None:
    """
    Add molecular descriptors to a DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.
        molcol (str): Column name containing RDKit molecule objects.
    """
    mol_descs = parallel_apply(df, calc_mol_descriptors, molcol)
    for desc in [
        "Num Ring",
        "Num Ar Ring",
        "Num ArHetcy",
        "Num Hetcy",
        "Num Hetatm",
        "Num Spiro",
        "Frac Sp3",
        "MR",
    ]:
        df[desc] = [desc_vals[desc] if desc_vals else None for desc_vals in mol_descs]
        if any(val is None for val in df[desc]):
            logging.warning(f"Descriptor {desc} has None values for some molecules.")