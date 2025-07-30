#!/usr/bin/env python3
import logging
from typing import Optional, Tuple, Dict
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, rdDistGeom, rdMolDescriptors
from concurrent.futures import ThreadPoolExecutor
from .util import parallel_apply, describe_mol

def needs_hydrogens(mol: Chem.Mol) -> bool:
    """Determine whether a molecule requires the addition of hydrogen atoms.
    
    Parameters:
        mol (rdkit.Chem.Mol): The RDKit molecule object.
    
    Returns:
        bool: True if the molecule has no hydrogen atoms, False otherwise.
    """
    return not any(atom.GetAtomicNum() == 1 for atom in mol.GetAtoms())

def configure_etkdg(random_seed: int, force_tolerance: float, prune_thresh: float) -> rdDistGeom.ETKDGv3:
    """
    Configure and return an ETKDG v3 parameter object for conformer generation.

    This function initializes the parameters for the ETKDGv3 method used in distance geometry
    calculations. It sets the random seed for reproducibility, enables multi-threading (using all available threads),
    activates the use of random coordinates, and configures both the optimizer's force tolerance and the RMS threshold
    for pruning conformations. Additionally, it enables small ring torsions which can be crucial for accurate geometry setups.

    Parameters:
        random_seed (int): An integer seed for initializing the random number generator, ensuring reproducible results.
        force_tolerance (float): The tolerance threshold for forces during geometric optimizations.
        prune_thresh (float): The RMS threshold value used for pruning unnecessary conformations.

    Returns:
        rdDistGeom.ETKDGv3: A configured instance of the ETKDGv3 parameters ready for conformer generation.
    """
    params = rdDistGeom.ETKDGv3()
    params.randomSeed = random_seed
    params.numThreads = 0 # Use all available threads
    params.useRandomCoords = True
    params.optimizerForceTol = force_tolerance
    params.useSmallRingTorsions = True
    params.pruneRmsThresh = prune_thresh
    params.maxIterations = 500
    return params

def calculate_conformer_energies(mol: Chem.Mol, conformer_ids: list[int]) -> Optional[Dict[int, float]]:
    """
    Calculate the MMFF energies for the specified conformers of a molecule in parallel.

    If any conformer fails, the entire molecule is marked as failed, and a single error message is logged.

    Parameters:
        mol (rdkit.Chem.Mol): The RDKit molecule with pre-computed 3D conformations.
        conformer_ids (List[int]): A list of conformer identifiers whose energies are to be calculated.

    Returns:
        Optional[Dict[int, float]]: A dictionary mapping each conformer identifier to its calculated MMFF energy,
        or None if the calculation fails for any conformer.
    """
    mmff_props = AllChem.MMFFGetMoleculeProperties(mol)
    
    def safe_calc_energy(conformer_id: int):
        try:
            ff = AllChem.MMFFGetMoleculeForceField(mol, mmff_props, confId=conformer_id)
            if ff is None:
                raise ValueError(f"Force field returned None for conformer {conformer_id}")
            return ff.CalcEnergy()
        except Exception as e:
            logging.info(f"Error calculating energy for conformer: {e}", exc_info=False)
            return None

    # Calculate energies for all conformers
    energies = {}
    for conformer_id in conformer_ids:
        energy = safe_calc_energy(conformer_id)
        if energy is None:
            logging.error(f"Failed to calculate energies of conformers of molecule: {describe_mol(mol)}")
            return None  # Fail the entire molecule if any conformer fails
        energies[conformer_id] = energy

    return energies

def filter_conformers(mol: Chem.Mol, energies: Dict[int, float], energy_range: float) -> Tuple[Chem.Mol, Dict[int, float]]:
    """
    Filter the conformers of a molecule based on an energy cutoff.
    This function selects conformers from the given molecule whose energy does not exceed the lowest energy 
    by more than a specified range and returns a new molecule containing only these valid conformers along with 
    their associated energies.
    
    Parameters:
        mol (Chem.Mol): The input RDKit molecule potentially containing multiple conformers.
        energies (Dict[int, float]): A dictionary mapping each conformer's identifier to its corresponding energy.
        energy_range (float): The maximum allowed energy difference from the lowest-energy conformer; only conformers 
                              within this threshold are kept.
                              
    Returns:
        Tuple[Chem.Mol, Dict[int, float]]:
            A tuple containing:
              - A new RDKit molecule that includes only those conformers meeting the energy criteria.
              - A dictionary with the conformer IDs and their energies for the retained conformers.
    """
    min_energy = min(energies.values())
    valid_ids = [conformer_id for conformer_id, energy in energies.items() if (energy - min_energy) <= energy_range]
    
    filtered_mol = Chem.Mol(mol)
    filtered_mol.RemoveAllConformers()
    for conformer_id in valid_ids:
        filtered_mol.AddConformer(Chem.Conformer(mol.GetConformer(conformer_id)))
    
    kept_energies = {conformer_id: energies[conformer_id] for conformer_id in valid_ids}
    return filtered_mol, kept_energies

def generate_conformers_and_optimize(
    mol: Chem.Mol,
    random_seed: int,
    force_tolerance: float,
    prune_thresh: float,
    num_conformers: int,
    energy_range: float,
) -> Tuple[Optional[Chem.Mol], Optional[Dict[int, float]]]:
    """
    Generate and optimize conformers for a molecule using ETKDGv3 parameters and MMFF energy evaluation.

    If any conformer fails during energy calculation, the entire molecule is marked as failed.

    Args:
        mol (Chem.Mol): RDKit molecule object.
        random_seed (int): Random seed for conformer generation.
        force_tolerance (float): Tolerance for the force convergence during conformer optimization.
        prune_thresh (float): RMSD threshold to prune similar conformers.
        num_conformers (int): Number of conformers to generate.
        energy_range (float): Maximum allowed energy difference (in kcal/mol) relative to the lowest-energy conformer.

    Returns:
        Tuple[Optional[Chem.Mol], Optional[Dict[int, float]]]:
            A tuple containing:
              - the molecule with only the filtered conformers,
              - a dictionary mapping conformer IDs to their calculated energies.
            Returns (None, None) if conformer generation or energy calculation fails.
    """
    try:
        # Input validation
        if not mol or num_conformers <= 0 or force_tolerance <= 0:
            logging.warning("Invalid input molecule or parameters.")
            return None, None

        # Log molecule details
        logging.info(f"Processing molecule: {describe_mol(mol)}")
        if needs_hydrogens(mol):
            logging.info(f"Adding hydrogens to the {describe_mol(mol)}.")
            mol = Chem.AddHs(mol)

        if not mol.GetNumAtoms():
            logging.warning("Molecule has no atoms.")
            return None, None

        # Generate conformers
        params = configure_etkdg(random_seed, force_tolerance, prune_thresh)
        conformer_ids = rdDistGeom.EmbedMultipleConfs(mol, num_conformers, params)
        if not conformer_ids:
            logging.warning("No conformers were generated for the molecule.")
            return None, None

        # Calculate and filter energies
        energies = calculate_conformer_energies(mol, conformer_ids)
        if energies is None:
            return None, None  # Fail the molecule if energy calculation fails
        
        return filter_conformers(mol, energies, energy_range)
        
    except Exception as e:
        logging.error(f"Conformer generation failed: {e}", exc_info=True)
        return None, None

def calc_geometry(
    mol: Chem.Mol, 
    energies: Dict[int, float],
) -> Tuple[float, float, str] | Tuple[None, None, None]:
    """
    Calculate geometry descriptors (npr1, npr2, and classification) using Boltzmann weighting
    based on pre-computed conformer energies.

    Args:
        mol (Chem.Mol): Molecule with conformers.
        energies (Dict[int, float]): Dictionary of conformer energies.

    Returns:
        Tuple containing:
            - NPR1 (float): Descriptor value NPR1.
            - NPR2 (float): Descriptor value NPR2.
            - geometry (str): String classification of the geometry.
        Returns (None, None, None) if an error occurs.
    """
    try:
        if not mol or not energies:
            return None, None, None

        # Ensure the molecule has conformers
        if mol.GetNumConformers() == 0:
            logging.warning(f"Molecule has no conformers: {describe_mol(mol)}")
            return None, None, None

        # Boltzmann weighting
        min_energy = min(energies.values())
        weights = {
            conformer_id: np.exp(-(energy - min_energy) / (0.001987 * 298.15))
            for conformer_id, energy in energies.items()
        }
        total = sum(weights.values())
        if total < 1e-10:  # Numerical stability check
            return None, None, None
            
        weights = {conformer_id: w/total for conformer_id, w in weights.items()}

        # Calculate weighted averages
        npr1 = sum(w * rdMolDescriptors.CalcNPR1(mol, confId=conformer_id) for conformer_id, w in weights.items())
        npr2 = sum(w * rdMolDescriptors.CalcNPR2(mol, confId=conformer_id) for conformer_id, w in weights.items())

        # Classify geometry
        geometry = "Balanced"
        if npr1 - npr2 > 0.5:
            geometry = "Rod-like"
        elif npr1 + npr2 > 1.5:
            geometry = "Sphere-like"
        elif npr2 < 0.75:
            geometry = "Disc-like"
            
        return npr1, npr2, geometry
        
    except Exception as e:
        logging.error(f"Geometry calculation failed: {e}", exc_info=True)
        return None, None, None


def add_geometry(
    df: pd.DataFrame,
    threedcol: str,
    random_seed: int,
    force_tolerance: float,
    prune_thresh: float,
    num_conformations: int,
    energy_range: float,
) -> None:
    """Update DataFrame with computed 3D geometries and corresponding energy properties.
    This function augments the provided pandas DataFrame with three-dimensional molecular conformers and
    their associated geometry descriptors. It generates multiple conformers for each molecule in the specified
    column, optimizes them given the provided energy parameters, and calculates geometric properties such as
    NPR1, NPR2, and an overall geometry descriptor.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing molecular data. Must include the column specified by `molcol`.
        molcol (str): Name of the column in the DataFrame that contains the molecular representations.
        threedcol (str): Name of the new column to be added to the DataFrame, which will store the optimized 3D geometries.
        random_seed (int): Seed for the random number generator used during conformer generation to ensure reproducibility.
        force_tolerance (float): Tolerance level for the forces during the geometry optimization process.
        prune_thresh (float): Pruning threshold to discard similar conformers and reduce redundancy.
        num_conformations (int): Maximum number of conformers to generate for each molecule.
        energy_range (float): Allowed energy window within which conformers are considered for further calculations.
        
    Raises:
        ValueError: If the specified molecular column (`molcol`) is not present in the DataFrame.
        
    Notes:
        - If the DataFrame is empty, the function logs a warning and terminates without modifying the DataFrame.
        - The function applies parallel processing to generate conformers and optimize geometries,
          ensuring efficient processing of potentially large datasets.
    """
    if threedcol not in df.columns:
        raise ValueError(f"Column {threedcol} not found in DataFrame")
    if df.empty:
        logging.warning("Empty DataFrame provided")
        return

    results = parallel_apply(
        df, 
        generate_conformers_and_optimize,
        column=threedcol,
        random_seed=random_seed,
        force_tolerance=force_tolerance,
        prune_thresh=prune_thresh,
        num_conformers=num_conformations,
        energy_range=energy_range
    )
    
    # Update the DataFrame with the filtered molecules
    for i, (filtered_mol, energies) in enumerate(results):
        if filtered_mol is not None and filtered_mol.GetNumConformers() > 0:
            df.at[i, threedcol] = filtered_mol  # Update the molecule with conformers
        else:
            logging.warning(f"Molecule at index {i} has no conformers: {describe_mol(df.at[i, threedcol])}")

    geom_props = [
        calc_geometry(mol, energies) if mol is not None and mol.GetNumConformers() > 0 else (None, None, None)
        for mol, energies in results
    ]
    while len(geom_props) < len(df):
        geom_props.append((None, None, None))  # Fill missing rows with None values

    # Assign geometry descriptors to the DataFrame
    df["NPR1"], df["NPR2"], df["Geometry"] = zip(*geom_props)