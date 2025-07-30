import pytest
import pandas as pd
from rdkit import Chem
from molmetrics.util import apply_func, parallel_apply, remove_substructure

def test_apply_func():
    result = apply_func(2, lambda x, y: x + y, {"y": 3})
    assert result == 5

def multiply_by_two(x):
    return x * 2

def test_parallel_apply():
    df = pd.DataFrame({"numbers": [1, 2, 3]})
    results = parallel_apply(df, multiply_by_two, "numbers")
    assert results == [2, 4, 6]

def test_remove_substructure():
    smiles = ["CCO", "CCN", "CCC"]
    df = pd.DataFrame({"ROMol": [Chem.MolFromSmiles(s) for s in smiles]})
    substructures = ["N"]
    result_df = remove_substructure(df, "ROMol", substructures)
    assert all(Chem.MolToSmiles(mol) != "CCN" for mol in result_df["Fragment"])
