#!/usr/bin/env python3
# -----------------------------------------------------
# Calculate QED scores, QED properties, molecular descriptors,
# and geometry descriptors from libraries of small molecules.
#
# Seth D. Veenbaas
# Weeks Lab, UNC-CH
# 2025
#
# Version 1.0.0
#
# -----------------------------------------------------

import pandas as pd
import argparse
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import PandasTools
import logging

from molmetrics.io import make_from_smiles, make_from_sdf, make_from_pickle, save_df
from molmetrics.util import remove_substructure
from molmetrics.qed import add_qed, add_qed_properties
from molmetrics.mol_describe import add_mol_descriptors
from molmetrics.geometry import add_geometry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("molmetrics.log"),
        logging.StreamHandler()
    ]
)


def get_mol_metrics(
    df: pd.DataFrame,
    molcol: str,
    threedcol: str,
    substructures: list | None,
    properties: bool,
    moldescriptor: bool,
    geometry: bool,
    random_seed: int,
    force_tolerance: float,
    prune_thresh: float,
    num_conformers: int,
    energy_range: float,
    out: str | Path,
    file: Path,
    no_img: bool,
) -> None:
    """
    Calculate all molecular metrics for a given DataFrame and save outputs in various formats.

    The function can remove specified substructures, calculate QED scores and properties,
    compute selected molecular descriptors, and (if requested) generate conformers to calculate geometry descriptors.
    The geometry routine uses ETKDGv3 for conformer generation with MMFF energy evaluation.

    Args:
        df (pd.DataFrame): Input DataFrame with molecular data.
        molcol (str): Column name containing RDKit molecule objects.
        threedcol (str): Column name for storing 3D molecule objects.
        substructures (list | None): List of SMARTS patterns to remove from molecules.
        properties (bool): Flag to add QED properties.
        moldescriptor (bool): Flag to add molecular descriptors.
        geometry (bool): Flag to add geometry descriptors.
        random_seed (int): Random seed for conformer generation.
        force_tolerance (float): Force convergence tolerance during optimization.
        prune_thresh (float): RMSD threshold for filtering similar conformers.
        num_conformers (int): Number of conformers to generate.
        energy_range (float): Allowed energy window (in kcal/mol) for filtering conformers.
        out (str | Path): Output directory path.
        file (Path): Input file path (for naming outputs).
        no_img (bool): Flag indicating whether to exclude 3D images from the output Excel.
    """
    molcol_list = ["ROMol"]
    if geometry:
        df['3DMol'] = df[molcol].copy()
        molcol_list = ["ROMol", "3DMol"]
    
    try:
        if substructures:
            logging.info("Removing substructures...")
            df = remove_substructure(df, molcol, substructures=substructures)
            molcol = "Fragment"
            # Changed to call EmbedMolecule on each molecule individually
            df["3DFragment"] = df[molcol].copy()
            threedcol = "3DFragment"
            molcol_list = ["ROMol", molcol, threedcol]
                
        # Add QED scores
        logging.info("Calculating QED score...")
        add_qed(df, molcol)
        
        # Add QED properties
        print(f'Properties: {properties}')
        if properties:
            logging.info("Calculating QED properties...")
            add_qed_properties(df, molcol)
        
        # Add select molecular descriptors
        if moldescriptor:
            logging.info("Calculating molecular descriptors...")
            add_mol_descriptors(df, molcol)
        
        # Generate conformers and add geometry descriptors
        if geometry:
            logging.info("Generating conformers and calculating geometry descriptors...")
            add_geometry(df, threedcol, random_seed, force_tolerance, prune_thresh, num_conformers, energy_range)
                
        save_df(df=df, out=out, file=file, molcol=molcol_list, threedcol=threedcol, no_img=no_img)
        
        logging.info("Done!")
    except Exception as e:
        logging.error(f"Error in get_mol_metrics: {e}", exc_info=True)
    
    return df


def process_file(file, column, substructures, properties, moldescriptors, geometry, random_seed, force_tolerance, prune_thresh, num_conformers, energy_range, out, no_img):
    """
    Process a single file and calculate molecular metrics.

    Args:
        file (Path): Input file path.
        column (str): Column name containing SMILES strings.
        substructures (list | None): Optional list of substructures to remove from molecules.
        properties (bool): Flag indicating whether to calculate QED properties.
        moldescriptors (bool): Flag indicating whether to include molecular descriptors.
        geometry (bool): Flag indicating whether to calculate geometry descriptors.
        random_seed (int): Random seed for ETKDGv3 conformer generation.
        force_tolerance (float): Force tolerance for conformer optimization.
        num_conformers (int): Number of conformers to generate.
        energy_range (float): Energy range (in kcal/mol) for Boltzmann averaging.
        out (str | Path): Output directory path.
        no_img (bool): Flag to exclude images in the output XLSX.
    """
    ext = file.suffix.lower()
    try:
        if ext == ".sdf":
            df, molcol, threedcol = make_from_sdf(file)
        elif ext in [".csv", ".xlsx"]:
            df, molcol, threedcol = make_from_smiles(file, column)
        elif ext == ".pkl":
            make_from_pickle(file, out, no_img)
            return
        else:
            logging.warning(f"Unsupported file type: {file}")
            return

        _ = get_mol_metrics(
            df,
            molcol,
            threedcol,
            substructures,
            properties,
            moldescriptors,
            geometry,
            random_seed,
            force_tolerance,
            prune_thresh,
            num_conformers,
            energy_range,
            out,
            file,
            no_img,
        )
    except Exception as e:
        logging.error(f"Error processing file {file}: {e}", exc_info=True)


def process_smiles(smiles_list, substructures, properties, moldescriptors, geometry, random_seed, force_tolerance, prune_thresh, num_conformers, energy_range, out, no_img):
    """
    Process a list of SMILES strings and calculate molecular metrics.

    Args:
        smiles_list (list[str]): List of SMILES strings.
        substructures (list | None): Optional list of substructures to remove from molecules.
        properties (bool): Flag indicating whether to calculate QED properties.
        moldescriptors (bool): Flag indicating whether to include molecular descriptors.
        geometry (bool): Flag indicating whether to calculate geometry descriptors.
        random_seed (int): Random seed for ETKDGv3 conformer generation.
        force_tolerance (float): Force tolerance for conformer optimization.
        num_conformers (int): Number of conformers to generate.
        energy_range (float): Energy range (in kcal/mol) for Boltzmann averaging.
        out (str | Path): Output directory path.
        no_img (bool): Flag to exclude images in the output XLSX.
    """
    try:
        data = {"SMILES": smiles_list}
        df = pd.DataFrame(data)
        molcol = "ROMol"
        threedcol = "3DMol"
        PandasTools.AddMoleculeColumnToFrame(df, smilesCol="SMILES", molCol=molcol, includeFingerprints=True)

        df = get_mol_metrics(
            df,
            molcol,
            threedcol,
            substructures,
            properties,
            moldescriptors,
            geometry,
            random_seed,
            force_tolerance,
            prune_thresh,
            num_conformers,
            energy_range,
            out,
            file="smiles_input",
            no_img=no_img,
        )
        
        # Exclude specified columns if they are present
        excluded_columns = ['ROMol', '3DMol', 'Fragment']
        df_to_display = df.drop(columns=[col for col in excluded_columns if col in df.columns])
        
        # Display the modified DataFrame as stdout
        print(df_to_display)
    except Exception as e:
        logging.error(f"Error processing SMILES strings: {e}", exc_info=True)


def parseArgs():
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    prs = argparse.ArgumentParser(description="Calculate QED scores from SMILES or SDF.")
    ex_group = prs.add_mutually_exclusive_group()

    ex_group.add_argument(
        "-d", "--directory", type=Path, help="Path to a directory containing input files (.sdf, .csv, .xlsx, .pkl)."
    )

    ex_group.add_argument(
        "-f", "--file", type=Path, nargs="+", help="Path(s) to input file(s) (.sdf, .csv, .xlsx, .pkl). Example: -f file1.sdf file2.csv"
    )
    
    ex_group.add_argument(
        "-m", "--molecule", type=str, nargs="+", help="SMILES strings of input molecules. Example: -f 'CCO' 'CCN'"
    )

    prs.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="Path to output directory. (Default=directory of input file)",
    )

    prs.add_argument(
        "-c",
        "--column",
        type=str,
        default="SMILES",
        help="Name/substring of column containing SMILES strings. (Default=SMILES)",
    )

    prs.add_argument(
        "-s",
        "--substructures",
        type=str,
        nargs="*",
        default=None,
        help="Provide SMARTS substructure to remove before calculating properties. \
             Use 'diazirine_handle' to remove diazarne FFF handles. \
             (Default=None)",
    )

    prs.add_argument(
        "-p",
        "--properties",
        action="store_true",
        default=False,
        help="Adds QED properties to outputs. (Default=False)",
    )

    prs.add_argument(
        "-md",
        "--moldescriptors",
        action="store_true",
        default=False,
        help="Adds selected molecular descriptors to outputs. (Default=False)",
    )

    prs.add_argument(
        "-g",
        "--geometry",
        action="store_true",
        default=False,
        help="Adds NPR1, NPR2, and geometry descriptor to outputs. \
            NOTE: This feature is resource intensive, \
            using the --conformers argument to decrease the required resources. \
            (Default=False)",
    )
    
    prs.add_argument(
        "-rs",
        "--random_seed",
        type=int,
        default=1789,
        help="Random seed for ETKDGv3 conformer generation. (Default=1789)",
    )
    
    prs.add_argument(
        "-ft",
        "--force_tolerance",
        type=float,
        default=0.001,
        help="Optimizer force tolerance for ETKDGv3 conformer optimization. \
            Use 0.0135 for faster performance. (Default=0.001)",
    )
    
    prs.add_argument(
        "-pt",
        "--prune_thresh",
        type=float,
        default=0.1,
        help="RMSD (Å) threshold for filtering conformers during ETKDGv3 generation. \
            Conformers below this threshold are discarded to reduce redundancy. (Default=0.1)",
    )
    
    prs.add_argument(
        "-cf",
        "--num_conformers",
        type=int,
        default=1000,
        help="Number of conformers to generate using ETKDGv3. (Default=1000)",
    )

    prs.add_argument(
        "-er",
        "--energy_range",
        type=float,
        default=3.0,
        help="Energy range in kcal/mol for Boltzmann averaging. (Default=3.0)",
    )

    prs.add_argument(
        "-ni",
        "--no_img",
        action="store_true",
        default=False,
        help="Include 3D molecule images from the output XLSX. (Default=False)",
    )

    args = prs.parse_args()
    if args.substructures == ["diazirine_handle"]:
        args.substructures = [
            "[#8]=[#6]-[#6]-[#6]-[#6]1(-[#6]-[#6]-[#6]#[#6])-[#7]=[#7]-1",
            "[#7]-[#6]-[#6]-[#6]1(-[#6]-[#6]-[#6]#[#6])-[#7]=[#7]-1",
            "[#6]-[#6]-[#6]1(-[#6]-[#6]-[#6]#[#6])-[#7]=[#7]-1",
        ]
    return args


def main(
    directory: str | Path,
    file: list[Path] | None,
    molecule: list[str] | None,
    out: str | Path,
    column: str,
    substructures: list | None,
    properties: bool,
    moldescriptors: bool,
    geometry: bool,
    random_seed: int,
    force_tolerance: float,
    prune_thresh: float,
    num_conformers: int,
    energy_range: float,
    no_img: bool,
):
    """
    Main function for processing input files and calculating molecular metrics.

    This function handles various input formats (SDF, CSV, XLSX, PKL) and applies
    relevant processing steps including substructure removal, QED scoring, addition
    of QED properties, calculation of molecular descriptors, and geometry descriptor
    computation. The parameters provided allow for configurable processing options,
    such as the number of conformers to generate and energy range for Boltzmann averaging.

    Args:
        directory (str | Path): Directory containing input files.
        file (list[Path] | None): List of input file paths.
        out (str | Path): Output directory path.
        column (str): Column name containing SMILES strings.
        substructures (list | None): Optional list of substructures to remove from molecules.
        properties (bool): Flag indicating whether to calculate QED properties.
        moldescriptors (bool): Flag indicating whether to include molecular descriptors.
        geometry (bool): Flag indicating whether to calculate geometry descriptors.
        random_seed (int): Random seed for ETKDGv3 conformer generation.
        force_tolerance (float): Force tolerance for conformer optimization.
        num_conformers (int): Number of conformers to generate.
        energy_range (float): Energy range (in kcal/mol) for Boltzmann averaging.
        no_img (bool): Flag to exclude images in the output XLSX.
    """
    try:
        if molecule:
            logging.info("Processing SMILES strings...")
            process_smiles(molecule, substructures, properties, moldescriptors, geometry, random_seed, force_tolerance, prune_thresh, num_conformers, energy_range, out, no_img)
            return

        files = []

        if directory:
            files += list(Path(directory).glob("*.sdf")) + \
                     list(Path(directory).glob("*.csv")) + \
                     list(Path(directory).glob("*.xlsx")) + \
                     list(Path(directory).glob("*.pkl"))

        if file:
            files += file

        for file in files:
            logging.info(f"Processing file: {file}")
            process_file(file, column, substructures, properties, moldescriptors, geometry, random_seed, force_tolerance, prune_thresh, num_conformers, energy_range, out, no_img)
    except Exception as e:
        logging.critical(f"Critical error in main: {e}", exc_info=True)
    
    
if __name__ == "__main__":
    main(**vars(parseArgs()))
