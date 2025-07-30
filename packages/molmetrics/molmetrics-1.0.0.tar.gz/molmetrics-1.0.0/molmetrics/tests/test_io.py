import pytest
import pandas as pd
from pathlib import Path
from molmetrics.io import make_from_smiles, make_from_sdf

def test_make_from_smiles(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("SMILES\nO=C1O[C@@H](CNC(=O)C)CN1c3cc(F)c(N2CCOCC2)cc3\nOC(=O)C1CCCN(C1)C(=O)C1(CC1)C1=CC=CC(Br)=C1\n")
    df, molcol, threedcol = make_from_smiles(csv_file, "SMILES")
    assert molcol and 'SMILES' in df.columns
    assert len(df) == 2

def test_make_from_sdf(tmp_path):
    sdf_file = tmp_path / "test.sdf"
    sdf_file.write_text("""
  RDKit          2D

 17 17  0  0  0  0            999 V2000
   -4.2867   -0.8250    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -3.5723   -0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -3.5723    0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -2.8578    0.8250    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -2.1433    0.4125    0.0000 N   0  0  0  0  0  0  0  0  0  0  0  0
   -2.1433   -0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.4290   -0.8250    0.0000 N   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7145   -0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7145    0.4125    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -0.0000   -0.8250    0.0000 N   0  0  0  0  0  0  0  0  0  0  0  0
    0.7145   -0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.4289   -0.8250    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    2.1433   -0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    2.8578   -0.8250    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    3.5722   -0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    4.2867    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -2.8578   -0.8250    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1   0  0  0  0
  2  3  1   0  0  0  0
  3  4  2   0  0  0  0
  4  5  1   0  0  0  0
  5  6  2   0  0  0  0
  6  7  1   0  0  0  0
  7  8  1   0  0  0  0
  8  9  2   0  0  0  0
  8 10  1   0  0  0  0
 10 11  1   0  0  0  0
 11 12  1   0  0  0  0
 12 13  1   0  0  0  0
 13 14  1   0  0  0  0
 14 15  1   0  0  0  0
 15 16  3   0  0  0  0
  6 17  1   0  0  0  0
  2 17  2   0  0  0  0
M  END
$$$$
""")
    df, molcol, threedcol = make_from_sdf(sdf_file)
    assert molcol in df.columns
    assert len(df) == 1
