#!/usr/bin/env python3
import pandas as pd
from rdkit import Chem
from rdkit.Chem import QED
from .util import parallel_apply
import logging

def add_qed(df: pd.DataFrame, molcol: str) -> None:
    """
    Add QED scores to a DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.
        molcol (str): Column name containing RDKit molecule objects.
    """
    df["QED"] = parallel_apply(df, QED.default, molcol)


def calc_qed_properties(mol: Chem.rdchem.Mol) -> dict | None:
    """
    Calculate QED properties for a molecule.

    Args:
        mol (Chem.Mol): RDKit molecule object.

    Returns:
        dict | None: Dictionary of QED properties or None if an error occurs.
    """
    try:
        properties = QED.properties(mol)
        return {
            "MW": properties[0],
            "ALOGP": properties[1],
            "HBA": properties[2],
            "HBD": properties[3],
            "PSA": properties[4],
            "ROTB": properties[5],
            "AROM": properties[6],
            "ALERTS": properties[7],
        }
    except Exception as e:
        logging.error(f"Error calculating QED properties: {e}", exc_info=True)
        return None

def add_qed_properties(
    df: pd.DataFrame,
    molcol: str,
) -> None:
    """
    Add QED properties to a DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.
        molcol (str): Column name containing RDKit molecule objects.
    """
    qed_props = parallel_apply(df, calc_qed_properties, molcol)
    for prop in ["MW", "ALOGP", "HBA", "HBD", "PSA", "ROTB", "AROM", "ALERTS"]:
        df[prop] = [props[prop] if props else None for props in qed_props]