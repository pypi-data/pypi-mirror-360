#!/usr/bin/env python3
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors
from concurrent.futures import ProcessPoolExecutor
import logging
from typing import Any, Callable

def apply_func(x: Any, func: Callable, kwargs: dict) -> Any:
    """
    Apply a function with arguments to a single input.

    Args:
        x (Any): Input data.
        func (Callable): Function to apply.
        kwargs (dict): Additional arguments for the function.

    Returns:
        Any: Result of the function application.
    """
    return func(x, **kwargs)


def parallel_apply(df: pd.DataFrame, func: Callable, column: str, **kwargs) -> list:
    """
    Apply a function to a DataFrame column in parallel.

    Args:
        df (pd.DataFrame): Input DataFrame.
        func (Callable): Function to apply.
        column (str): Column name to apply the function to.
        kwargs: Additional arguments for the function.

    Returns:
        list: Results of the function application.
    """
    try:
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(apply_func, df[column], [func] * len(df), [kwargs] * len(df)))
        return results
    except Exception as e:
        logging.error(f"Error in parallel_apply: {e}", exc_info=True)
        raise


def remove_substructure(
    df: pd.DataFrame, molcol: str, substructures: list[str] | None
) -> pd.DataFrame:
    """
    Remove specified substructures from molecules in a DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.
        molcol (str): Column name containing RDKit molecule objects.
        substructures (list[str] | None): List of SMARTS patterns for substructures to remove.

    Returns:
        pd.DataFrame: DataFrame with substructures removed.

    Note:
        This function creates and overwrites a "Fragment" column in the DataFrame.
    """
    try:
        if substructures is None:
            return df
        df["Fragment"] = df[molcol].copy()
        for substructure in substructures:
            if substructure:
                substructure = Chem.MolFromSmarts(substructure)
                df["Fragment"] = df["Fragment"].apply(lambda x: AllChem.DeleteSubstructs(x, substructure))
        df["Fragment"].apply(lambda x: AllChem.EmbedMolecule(Chem.AddHs(x)))
        df["Fragment"].apply(lambda x: Chem.SanitizeMol(x))
        return df
    except Exception as e:
        logging.error(f"Error in remove_substructure: {e}", exc_info=True)
        raise


def is_valid_molecule(mol: Chem.Mol) -> bool:
    """
    Check if a molecule is valid.

    Args:
        mol (Chem.Mol): RDKit molecule object.

    Returns:
        bool: True if the molecule is valid, False otherwise.
    """
    return mol is not None and isinstance(mol, Chem.Mol)


def describe_mol(mol):
    """Get comprehensive description of an RDKit molecule"""
    if not mol:
        return "Invalid molecule"
    
    return " ".join([
        f"SMILES: {Chem.MolToSmiles(Chem.RemoveHs(mol))}",
        f"Formula: {rdMolDescriptors.CalcMolFormula(mol)}",
        f"Mass: {rdMolDescriptors.CalcExactMolWt(mol):.2f}"
    ])