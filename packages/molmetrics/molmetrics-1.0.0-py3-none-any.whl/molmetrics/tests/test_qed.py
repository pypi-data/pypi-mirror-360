import pytest
import pandas as pd
from rdkit import Chem
from molmetrics.qed import add_qed, calc_qed_properties

def test_add_qed():
    smiles = ["O=C1O[C@@H](CNC(=O)C)CN1c3cc(F)c(N2CCOCC2)cc3", "OC(=O)C1CCCN(C1)C(=O)C1(CC1)C1=CC=CC(Br)=C1"]
    df = pd.DataFrame({"ROMol": [Chem.MolFromSmiles(s) for s in smiles]})
    add_qed(df, "ROMol")
    assert "QED" in df.columns
    assert all(df["QED"] > 0.89)

def test_calc_qed_properties():
    mol = Chem.MolFromSmiles("O=C1O[C@@H](CNC(=O)C)CN1c3cc(F)c(N2CCOCC2)cc3")
    properties = calc_qed_properties(mol)
    assert properties is not None
    assert "MW" in properties
    assert round(properties["MW"], 3) == 337.351
    assert "ALOGP" in properties
    assert round(properties["ALOGP"], 3) == 1.124
