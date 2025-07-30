#!/usr/bin/env python3
import pickle
import pandas as pd
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import PandasTools
from PIL import PngImagePlugin
import logging
import numpy as np

from .util import is_valid_molecule

# Increase the PngImagePlugin.MAX_TEXT_CHUNK limit to 4 GB
PngImagePlugin.MAX_TEXT_CHUNK = 4 * 1024 * 1024 * 1024

### PandasTools settings
PandasTools.InstallPandasTools()
PandasTools.RenderImagesInAllDataFrames(images=True)


def make_dataframe(file: Path):
    """
    Reads a file (CSV or XLSX) into a Pandas DataFrame.

    Args:
        file (Path): The path to the file (.csv or .xlsx) to read.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the all the data from the file.
    """
    try:
        extension = file.suffix.lower()
        if extension == ".csv":
            return pd.read_csv(file)
        elif extension == ".xlsx":
            return pd.read_excel(file)
        else:
            raise ValueError(f"Unsupported file format: {file}")
    except Exception as e:
        logging.error(f"Error reading file {file}: {e}", exc_info=True)
        raise

def make_from_smiles(
    csv: str | Path,
    column: str,
):
    """
    Create a DataFrame from a CSV file containing SMILES strings.

    Args:
        csv (str | Path): Path to the CSV file.
        column (str): Column name or substring containing SMILES strings.

    Returns:
        tuple: A tuple containing the DataFrame, molecule column name, and 3D molecule column name.
    """
    try:
        smiles_df = make_dataframe(csv)
        smiles_col = next(
            col for col in smiles_df.columns if column.lower() in col.lower()
        )
        smiles_df[smiles_col] = smiles_df[smiles_col].astype(str)

        molcol = "ROMol"
        threedcol = "3DMol"
        PandasTools.AddMoleculeColumnToFrame(
            smiles_df, smilesCol=smiles_col, molCol=molcol, includeFingerprints=True
        )

        # filters dataframe for organic molecules
        smiles_df = smiles_df.dropna(subset=[molcol])
        smiles_df = smiles_df[
            smiles_df[molcol].apply(lambda x: x.HasSubstructMatch(Chem.MolFromSmiles("C")))
        ]
        
        return smiles_df, molcol, threedcol
    except StopIteration:
        logging.error(f"Column containing '{column}' not found in {csv}.", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Error processing SMILES file {csv}: {e}", exc_info=True)
        raise

def make_from_sdf(
    sdf: str | Path,
):
    """
    Create a DataFrame from an SDF file.

    Args:
        sdf (str | Path): Path to the SDF file.

    Returns:
        tuple: A tuple containing the DataFrame, molecule column name, and 3D molecule column name.
    """
    try:
        name = Path(sdf).stem
        string_sdf = str(sdf)

        molcol = "ROMol"
        threedcol = "3DMol"
        sdf_df = PandasTools.LoadSDF(
            string_sdf,
            idName="ID",
            molColName=molcol,
            includeFingerprints=False,
            isomericSmiles=True,
            smilesName="SMILES",
            embedProps=True,
            removeHs=False,
            strictParsing=True,
        )

        if sdf_df.empty or molcol not in sdf_df.columns:
            raise ValueError("Failed to parse SDF file or missing 'ROMol' column.")

        # Filter DataFrame for organic molecules
        sdf_df = sdf_df.dropna(subset=[molcol])
        sdf_df = sdf_df[
            sdf_df[molcol].apply(lambda x: x.HasSubstructMatch(Chem.MolFromSmiles("C")))
        ]

        return sdf_df, molcol, threedcol
    except Exception as e:
        logging.error(f"Error processing SDF file {sdf}: {e}", exc_info=True)
        raise


def make_from_pickle(
    pickle: str | Path,
    out: str | Path,
    no_img: bool,
):
    """
    Process a pickle file and save its contents to an Excel file.

    Args:
        pickle (str | Path): Path to the pickle file.
        out (str | Path): Output directory path.
        no_img (bool): Whether to exclude images in the output.
    """
    df = pd.read_pickle(pickle)
    if out:
        dir = Path(out)
    else:
        dir = Path(pickle).parent
    if not dir.is_dir():
        dir.mkdir(parents=True, exist_ok=True)
    try:
        if no_img:
            df.to_excel(Path(dir) / (pickle.stem + "_qed.xlsx"), index=False)
        else:
            PandasTools.SaveXlsxFromFrame(df, Path(dir) / (pickle.stem + "_qed.xlsx"), molCol=["ROMol", "3DMol"], size=(150, 150))
    except Exception as e:
        logging.error(f"Unable to save .XLSX file: {e}", exc_info=True)


def save_df(
    df: pd.DataFrame,
    out: str | Path,
    file: str | Path,
    molcol: str | list,
    threedcol: str,
    no_img: bool,
):
    """
    Save a DataFrame to various output formats (SDF, HTML, Excel, and pickle).

    Args:
        df (pd.DataFrame): DataFrame to save.
        out (str | Path): Output directory path.
        file (str | Path): Input file path for naming outputs.
        molcol (str | list): Column(s) containing RDKit molecule objects.
        no_img (bool): Whether to exclude images in the Excel output.
    """
    try:
        if out:
            dir = Path(out)
        else:
            dir = Path(file).parent
        if not dir.is_dir():
            dir.mkdir(parents=True, exist_ok=True)
        file_name = Path(file).stem
        sdf_out = str(Path(dir, file_name + "_qed.sdf"))

        # Ensure the molecule column contains valid RDKit molecule objects
        valid_molcol = molcol[-1]
        df = df[df[valid_molcol].apply(is_valid_molecule)]

        # Write the SDF file
        excluded_columns = ['ROMol', '3DMol', 'Fragment']
        properties = [col for col in df.columns if col not in excluded_columns]
        PandasTools.WriteSDF(df, sdf_out, molColName=valid_molcol, properties=properties)
        logging.info(f"Saved SDF file: {sdf_out}")

        # Save HTML
        html_out = Path(dir, file_name + "_qed.html")
        df.to_html(html_out)
        logging.info(f"Saved HTML file: {html_out}")

        # Save pickle
        pickle_out = Path(dir, file_name + "_conformers.pkl")
        with open(pickle_out, 'wb') as f:
            pickle.dump(df, f)
        logging.info(f"Saved pickle file: {pickle_out}")

        # Save Excel
        excel_out = Path(dir, file_name + "_qed.xlsx")
        try:
            # Replace NaN and Inf values
            cleaned_df = df.replace([np.nan, np.inf, -np.inf], "")
            if no_img:
                cleaned_df.to_excel(excel_out, index=False)
            else:
                # Safeguard: Exclude rows with invalid molecules before saving
                valid_df = cleaned_df[cleaned_df[valid_molcol].apply(is_valid_molecule)]
                if valid_df.empty:
                    logging.warning("No valid molecules found for Excel export.")
                    valid_df.to_excel(excel_out, index=False)  # Save without images
                else:
                    try:
                        PandasTools.SaveXlsxFromFrame(valid_df, excel_out, molCol=molcol, size=(150, 150))
                    except Exception as img_error:
                        logging.error(f"Error generating molecule images for Excel: {img_error}", exc_info=True)
                        valid_df.to_excel(excel_out, index=False)  # Fallback to saving without images
            logging.info(f"Saved Excel file: {excel_out}")
        except Exception as e:
            logging.error(f"Error saving Excel file: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"Error saving DataFrame: {e}", exc_info=True)