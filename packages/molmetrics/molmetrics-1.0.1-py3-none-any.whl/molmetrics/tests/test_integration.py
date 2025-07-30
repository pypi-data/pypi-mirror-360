import subprocess
from pathlib import Path
import filecmp
from rdkit import Chem
import pytest

def test_molmetrics_integration(tmp_path):
    """
    Integration test for molmetrics.

    This test runs the molmetrics command with specific arguments and compares
    the generated output file with the expected results.
    """
    # Paths
    input_file = Path(__file__).parent.parent / "data" / "mini_test_library.sdf"
    expected_output_file = Path(__file__).parent.parent / "data" / "mini_test_library_output" / "mini_test_library_qed_reference.sdf"
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()

    # Command to run
    command = [
        "python", "-m", "molmetrics",
        "-f", str(input_file),
        "-p", "-md", "-g",
        "-o", str(output_dir),
        "-s", "[#7]-[#6]-[#6]-[#6]-[#6]C#C", "[#6]C#C"
    ]

    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)

    # Assert the command ran successfully
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"

    # Verify the output file exists
    generated_output_file = output_dir / "mini_test_library_qed.sdf"
    assert generated_output_file.exists(), "Output file was not generated."
    assert generated_output_file.stat().st_size > 0, "Output file is empty."

    # Load molecules from generated and reference SDFs
    gen_mols = [mol for mol in Chem.SDMolSupplier(str(generated_output_file)) if mol is not None]
    ref_mols = [mol for mol in Chem.SDMolSupplier(str(expected_output_file)) if mol is not None]

    assert len(gen_mols) == 5, f"Expected 5 molecules in generated output, found {len(gen_mols)}"
    assert len(ref_mols) == 5, f"Expected 5 molecules in reference output, found {len(ref_mols)}"

    for i, (gen_mol, ref_mol) in enumerate(zip(gen_mols, ref_mols)):
        # Compare molecule SMILES if present
        gen_SMILES = gen_mol.GetProp("SMILES") if gen_mol.HasProp("SMILES") else ""
        ref_SMILES = ref_mol.GetProp("SMILES") if ref_mol.HasProp("SMILES") else ""
        assert gen_SMILES == ref_SMILES, f"Molecule {i} SMILES mismatch: {gen_SMILES} != {ref_SMILES}"

        # Compare MW
        gen_mw = float(gen_mol.GetProp("MW"))
        ref_mw = float(ref_mol.GetProp("MW"))
        assert gen_mw == pytest.approx(ref_mw, rel=0.005), f"Molecule {i} MW mismatch: {gen_mw} != {ref_mw}"

        # Compare QED
        gen_qed = float(gen_mol.GetProp("QED"))
        ref_qed = float(ref_mol.GetProp("QED"))
        assert gen_qed == pytest.approx(ref_qed, rel=0.005), f"Molecule {i} QED mismatch: {gen_qed} != {ref_qed}"
