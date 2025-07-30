import pytest
from rdkit import Chem
from molmetrics.geometry import generate_conformers_and_optimize, calc_geometry

def test_generate_conformers_and_optimize():
    mol = Chem.MolFromSmiles("O=C1O[C@@H](CNC(=O)C)CN1c3cc(F)c(N2CCOCC2)cc3")
    result_mol, energies = generate_conformers_and_optimize(
        mol, random_seed=42, force_tolerance=0.001, prune_thresh=0.1, num_conformers=10, energy_range=3.0
    )
    assert result_mol is not None
    assert energies is not None
    assert len(energies) > 0

def test_calc_geometry():
    mol = Chem.MolFromSmiles("O=C1O[C@@H](CNC(=O)C)CN1c3cc(F)c(N2CCOCC2)cc3")
    result_mol, energies = generate_conformers_and_optimize(
        mol, random_seed=42, force_tolerance=0.001, prune_thresh=0.1, num_conformers=10, energy_range=3.0
    )
    npr1, npr2, geometry = calc_geometry(result_mol, energies)
    assert npr1 == pytest.approx(0.088, abs=0.075)
    assert npr2 == pytest.approx(0.95, abs=0.075)
