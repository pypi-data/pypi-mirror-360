# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 as Unilever Global IP Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Data processing and validation functions for BIFROST analysis.

This module provides functions for:
- Data validation (meta data, counts, configuration)
- Data processing and filtering
- Batch processing and archiving
- Input/output operations
"""

import itertools
import os
import pickle
import shutil
import tarfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from bifrost_httr.utils.logging import get_logger

logger = get_logger(__name__)

# Constants
COUNT_THRESHOLD = 100  # Threshold for splitting counts into high and low categories
MAX_PERCENT_MAPPED_READS = 100  # Maximum allowed percentage for mapped reads
MIN_REQUIRED_COLUMNS = 2  # Minimum required columns (probe ID and counts)


# Validation Functions
def validate_meta_data(
    meta: pd.DataFrame,
    meta_mapper_dict: dict[str, list[str]] | None = None,
) -> None:
    """Validate meta data DataFrame.

    Args:
        meta: Meta data DataFrame to validate
        meta_mapper_dict: Optional dictionary mapping output columns to input columns.
                         If provided, validation will check for mapped column names.

    Raises:
        ValueError: If required columns are missing or data is invalid

    """
    # Define required columns based on mapper if provided
    if meta_mapper_dict is not None:
        required_columns = list(meta_mapper_dict.keys())
    else:
        required_columns = [
            "Test substance",
            "Concentration",
            "Sample ID",
            "Num. mapped reads",
            "Percent mapped reads",
        ]

    # Check for required columns
    missing_columns = [col for col in required_columns if col not in meta.columns]
    if missing_columns:
        error_msg = f"Missing required columns in meta data: {missing_columns}"
        raise ValueError(error_msg)

    # Validate concentration values if present
    if "Concentration" in meta.columns and not np.all(meta["Concentration"] >= 0):
        error_msg = "Concentration values must be non-negative"
        raise ValueError(error_msg)

    # Validate read counts if present
    if "Num. mapped reads" in meta.columns and not np.all(
        meta["Num. mapped reads"] >= 0,
    ):
        error_msg = "Num. mapped reads must be non-negative"
        raise ValueError(error_msg)
    if "Percent mapped reads" in meta.columns and not np.all(
        (meta["Percent mapped reads"] >= 0)
        & (meta["Percent mapped reads"] <= MAX_PERCENT_MAPPED_READS),
    ):
        error_msg = (
            f"Percent mapped reads must be between 0 and {MAX_PERCENT_MAPPED_READS}"
        )
        raise ValueError(error_msg)


def validate_counts_table(counts: pd.DataFrame) -> None:
    """Validate counts table DataFrame.

    Args:
        counts: Counts table DataFrame to validate

    Raises:
        ValueError: If data is invalid

    """
    # Check for probe column
    if counts.shape[1] < MIN_REQUIRED_COLUMNS:
        error_msg = f"Counts table must have at least {MIN_REQUIRED_COLUMNS} columns (probe ID and counts)"
        raise ValueError(
            error_msg,
        )

    # Validate count values
    count_columns = counts.columns[1:]
    if not np.all(counts[count_columns].to_numpy() >= 0):
        error_msg = "Count values must be non-negative"
        raise ValueError(error_msg)


def validate_config(config: dict[str, Any]) -> None:
    """Validate configuration dictionary.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ValueError: If configuration is invalid

    """
    required_keys = [
        "Minimum percent mapped reads",
        "Minimum number mapped reads",
        "Minimum average treatment count",
        "Batch key",
    ]

    # Check for required keys
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        error_msg = f"Missing required configuration keys: {missing_keys}"
        raise ValueError(error_msg)

    # Validate numeric values
    if not isinstance(config["Minimum percent mapped reads"], (int | float)) or not (
        0 <= config["Minimum percent mapped reads"] <= MAX_PERCENT_MAPPED_READS
    ):
        error_msg = f"Minimum percent mapped reads must be a number between 0 and {MAX_PERCENT_MAPPED_READS}"
        raise ValueError(
            error_msg,
        )

    if (
        not isinstance(config["Minimum number mapped reads"], int)
        or config["Minimum number mapped reads"] < 0
    ):
        error_msg = "Minimum number mapped reads must be a non-negative integer"
        raise ValueError(error_msg)

    if (
        not isinstance(config["Minimum average treatment count"], int)
        or config["Minimum average treatment count"] < 0
    ):
        error_msg = "Minimum average treatment count must be a non-negative integer"
        raise ValueError(
            error_msg,
        )

    # Validate batch key
    if not isinstance(config["Batch key"], str):
        error_msg = "Batch key must be a string"
        raise TypeError(error_msg)


def validate_filter_dict(filter_dict: dict[str, str], meta: pd.DataFrame) -> None:
    """Validate filter dictionary against meta data.

    Args:
        filter_dict: Filter dictionary to validate
        meta: Meta data DataFrame to validate against

    Raises:
        ValueError: If filters are invalid

    """
    # Check for required keys
    if "Test substance" not in filter_dict:
        error_msg = "Filter dictionary must contain 'Test substance' key"
        raise ValueError(error_msg)

    # Validate filter values exist in meta data
    for key, value in filter_dict.items():
        if key != "N/A" and key in meta.columns and value not in meta[key].to_numpy():
            error_msg = f"Filter value '{value}' not found in meta data column '{key}'"
            raise ValueError(
                error_msg,
            )


def validate_output_directory(output_dir: str | Path) -> None:
    """Validate output directory.

    Args:
        output_dir: Output directory path to validate

    Raises:
        ValueError: If directory is invalid
        PermissionError: If directory cannot be created

    """
    output_path = Path(output_dir)

    # Check if directory exists and is writable
    if output_path.exists() and not output_path.is_dir():
        error_msg = f"Output path exists but is not a directory: {output_dir}"
        raise ValueError(error_msg)
    if not os.access(output_path, os.W_OK):
        error_msg = f"No write permission for output directory: {output_dir}"
        raise PermissionError(
            error_msg,
        )

    # Try to create directory
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except PermissionError as err:
        error_msg = f"Cannot create output directory: {output_dir}"
        raise PermissionError(error_msg) from err


def validate_config_file(config_dict: dict[str, Any]) -> None:
    """Validate configuration file dictionary.

    Args:
        config_dict: Configuration dictionary containing test substances, cell types, and optional parameters

    Raises:
        ValueError: If required keys are missing or data is invalid

    """
    required_keys = [
        "Test substances",
        "Cell types",
        # other keys are optional and can be overridden by CLI
    ]

    # Check for required keys
    missing_keys = [key for key in required_keys if key not in config_dict]
    if missing_keys:
        error_msg = f"Missing required keys in configuration file: {missing_keys}"
        raise ValueError(
            error_msg,
        )

    # Validate test substances
    if not isinstance(config_dict["Test substances"], list) or not all(
        isinstance(x, str) for x in config_dict["Test substances"]
    ):
        error_msg = "Test substances must be a list of strings"
        raise ValueError(error_msg)

    # Validate cell types
    if not isinstance(config_dict["Cell types"], list) or not all(
        isinstance(x, str) for x in config_dict["Cell types"]
    ):
        error_msg = "Cell types must be a list of strings"
        raise ValueError(error_msg)

    # Check if Additional divider is present and has correct type
    if "Additional divider" in config_dict and not isinstance(
        config_dict["Additional divider"],
        str,
    ):
        error_msg = "Additional divider must be a string if present"
        raise ValueError(error_msg)

    # Check if Specific filters is present and has correct type
    if (
        "Specific filters" in config_dict
        and config_dict["Specific filters"] is not None
        and not isinstance(config_dict["Specific filters"], dict)
    ):
        error_msg = "Specific filters must be a dictionary if present and not None"
        raise ValueError(error_msg)

    # Validate optional numeric parameters if present
    if "Minimum percent mapped reads" in config_dict and (
        not isinstance(config_dict["Minimum percent mapped reads"], (int, float))
        or not (
            0 <= config_dict["Minimum percent mapped reads"] <= MAX_PERCENT_MAPPED_READS
        )
    ):
        error_msg = f"Minimum percent mapped reads must be a number between 0 and {MAX_PERCENT_MAPPED_READS}"
        raise ValueError(error_msg)

    if "Minimum number mapped reads" in config_dict and (
        not isinstance(config_dict["Minimum number mapped reads"], int)
        or config_dict["Minimum number mapped reads"] < 0
    ):
        error_msg = "Minimum number mapped reads must be a non-negative integer"
        raise ValueError(error_msg)

    if "Minimum average treatment count" in config_dict and (
        not isinstance(config_dict["Minimum average treatment count"], int)
        or config_dict["Minimum average treatment count"] < 0
    ):
        error_msg = "Minimum average treatment count must be a non-negative integer"
        raise ValueError(error_msg)

    if "Batch key" in config_dict and not isinstance(config_dict["Batch key"], str):
        error_msg = "Batch key must be a string"
        raise ValueError(error_msg)

    if "Random seed" in config_dict and not isinstance(config_dict["Random seed"], int):
        error_msg = "Random seed must be an integer"
        raise ValueError(error_msg)


# Data Processing Functions
def filter_percent_mapped_reads(
    df: pd.DataFrame,
    minimum_percent_mapped_reads: float,
) -> pd.DataFrame:
    """Filter out samples below the specified minimum percentage of mapped reads.

    Args:
        df: Input DataFrame
        minimum_percent_mapped_reads: Minimum percentage threshold

    Returns:
        Filtered DataFrame

    """
    return df[df["Percent mapped reads"] >= minimum_percent_mapped_reads]


def filter_total_mapped_reads(
    df: pd.DataFrame,
    minimum_total_mapped_reads: float,
) -> pd.DataFrame:
    """Filter out samples below the specified minimum total mapped reads.

    Args:
        df: Input DataFrame
        minimum_total_mapped_reads: Minimum total mapped reads threshold

    Returns:
        Filtered DataFrame

    """
    return df[df["Num. mapped reads"] >= minimum_total_mapped_reads]


def process_data(
    input_file_path: str | Path,
    path_to_output: str | Path,
    *,
    testing_mode: bool = False,
) -> None:
    """Process raw count data into a stan-compatible format for each probe.

    Args:
        input_file_path: Path to pipeline input json file
        path_to_output: Path to the temporary directory where intermediate output will be stored
        testing_mode: If True, only process the first probe for testing purposes

    Returns:
        None

    Raises:
        FileNotFoundError: If json file doesn't exist
        ValueError: If required fields are missing or invalid
        IndexError: If array dimensions don't match (e.g. counts matrix columns != total_count length)

    Notes:
        The input JSON file is expected to contain arrays with matching dimensions:
        - counts matrix columns should match total_count length
        - counts matrix columns should match batch_index length
        - counts matrix columns should match concentration length
        - counts matrix rows should match probes length
    """
    # Create directories for intermediate output within specified analysis directory
    output_path = Path(path_to_output)
    data_dir = output_path / "Data"
    fits_dir = output_path / "Fits"

    data_dir.mkdir(parents=True, exist_ok=True)
    fits_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    if not Path(input_file_path).exists():
        error_msg = "json does not exist"
        raise FileNotFoundError(error_msg)

    df = pd.read_json(input_file_path, typ="series", orient="index")

    count_matrix = np.array(df["counts"], dtype="int")
    n_sample = count_matrix.shape[1]

    if "total_count" not in df.index:
        total_count = np.sum(count_matrix, axis=0)
    else:
        total_count = np.array(df["total_count"], dtype="int")

    # Determine number of batches
    batch_index = np.array(df["batch_index"], dtype="int")
    n_batch = np.max(batch_index)
    n_treatment_batch = df["n_treatment_batch"]

    # Calculate concentration index for each sample
    n = len(total_count)
    concentration = np.array(df["concentration"], dtype="float")
    unique_concentration = list(np.unique(concentration[concentration > 0]))
    n_conc = len(unique_concentration)
    concentration_index = np.zeros(n, dtype="int")
    for i, j in enumerate(concentration):
        if j in unique_concentration:
            concentration_index[i] = unique_concentration.index(j) + 1
    unique_concentration = np.log10(unique_concentration)

    for probe_index, (probe, probe_count) in enumerate(
        zip(df["probes"], count_matrix, strict=False),
    ):
        if testing_mode and probe_index > 0:
            break

        # Split counts by high and low
        low_count_index = np.where(probe_count <= COUNT_THRESHOLD)[0] + 1
        high_count_index = np.where(probe_count > COUNT_THRESHOLD)[0] + 1
        n_low_count = len(low_count_index)
        n_high_count = len(high_count_index)

        data: dict[str, Any] = {
            "n_sample": n_sample,
            "n_treatment_batch": n_treatment_batch,
            "count": probe_count,
            "total_count": total_count,
            "n_batch": n_batch,
            "batch_index": batch_index,
            "n_conc": n_conc,
            "conc": unique_concentration,
            "conc_index": concentration_index,
            "n_low_count": n_low_count,
            "low_count_index": low_count_index,
            "n_high_count": n_high_count,
            "high_count_index": high_count_index,
        }

        with (data_dir / f"{probe}.pkl").open("wb") as f:
            pickle.dump(data, f)


# Batch Processing Functions
def create_manifest(
    batch_files: list[str],
    manifest_path: Path,
    tar_filename: str,
    batch_num: int,
) -> None:
    """Create a manifest file entry for a batch of files."""
    # If file doesn't exist, create it with header
    if not manifest_path.exists():
        with manifest_path.open("w") as f:
            f.write("batch\ttar_file\tprobes\n")

    # Get all probe names for this batch
    probe_names = [Path(file).stem for file in batch_files]
    # Join them with commas
    probes_str = ",".join(probe_names)

    with manifest_path.open("a") as f:
        f.write(f"{batch_num}\t{tar_filename}\t{probes_str}\n")


def create_tar_archive(files: list[str], output_path: Path) -> None:
    """Create a tar.gz archive from a list of files."""
    with tarfile.open(output_path, "w:gz") as tar:
        for file in files:
            tar.add(file, arcname=Path(file).name)


def create_directory_archive(files: list[str], output_path: Path) -> None:
    """Create a directory containing the files."""
    output_path.mkdir(parents=True, exist_ok=True)
    for file in files:
        # Copy file to output directory
        shutil.copy2(file, output_path / Path(file).name)


def process_batches(
    data_dir: Path,
    output_dir: Path,
    prefix: str,
    batch_size: int,
    batch_mode: str,
    archive_mode: str = "tar",
) -> Path:
    """Process the pickle files into batches and create manifests and archives.

    Args:
        data_dir: Directory containing the pickle files
        output_dir: Output directory where outputs should be created
        prefix: Prefix for output files
        batch_size: Number of files per batch
        batch_mode: Either 'batch' or 'all' to control archiving behavior
        archive_mode: Either 'tar' or 'directory' to control how files are stored

    Returns:
        Path: Path to the created manifest file

    Raises:
        FileNotFoundError: If no pickle files are found in the data directory
        ValueError: If archive_mode is not 'tar' or 'directory'

    """
    if archive_mode not in ["tar", "directory"]:
        error_msg = "archive_mode must be either 'tar' or 'directory'"
        raise ValueError(error_msg)

    # Get list of all pickle files
    files = sorted(data_dir.glob("*.pkl"))
    total_files = len(files)

    if not files:
        error_msg = f"No pickle files found in {data_dir}"
        raise FileNotFoundError(error_msg)

    # Create single manifest file in the output directory
    manifest_path = output_dir / f"{prefix}.manifest.csv"
    # Clear the manifest file if it exists
    manifest_path.unlink(missing_ok=True)

    # Create single archive if batch_mode is 'all'
    if batch_mode == "all":
        archive_name = f"{prefix}_batch0"
        if archive_mode == "tar":
            archive_path = output_dir / f"{archive_name}.tar.gz"
            create_tar_archive(files, archive_path)
        else:  # directory mode
            archive_path = output_dir / f"{archive_name}_dir"
            create_directory_archive(files, archive_path)

        # Process files in batches for manifest, even though we're using a single archive
        batch_num = 1
        for i in range(0, total_files, batch_size):
            batch_files = files[i : i + batch_size]
            create_manifest(batch_files, manifest_path, str(archive_path), batch_num)
            batch_num += 1
        return manifest_path

    # Process files in batches
    batch_num = 1
    for i in range(0, total_files, batch_size):
        batch_files = files[i : i + batch_size]
        batch_prefix = f"{prefix}_batch{batch_num}"

        if archive_mode == "tar":
            archive_path = output_dir / f"{batch_prefix}.tar.gz"
            create_tar_archive(batch_files, archive_path)
        else:  # directory mode
            archive_path = output_dir / batch_prefix
            create_directory_archive(batch_files, archive_path)

        # Add entries to manifest
        create_manifest(batch_files, manifest_path, str(archive_path), batch_num)
        batch_num += 1

    return manifest_path


# Input/Output Functions
def write_bifrost_input(
    meta: pd.DataFrame,
    filter_dict: dict[str, str],
    counts_table: pd.DataFrame,
    config_dict: dict[str, Any],
    output_directory: str | Path,
) -> None:
    """Apply filters to DataFrame and write BIFROST HTTr pipeline input.

    Args:
        meta: Meta data DataFrame
        filter_dict: Dictionary of filters to apply
        counts_table: Counts data DataFrame
        config_dict: Configuration dictionary
        output_directory: Directory to write output files

    Raises:
        ValueError: If no data matches the filters, if no data passes the filters,
                   or if no probes pass the filtering criteria
    """
    # Validate filter dictionary
    validate_filter_dict(filter_dict, meta)

    # Filter meta data
    test_substance_mask = meta["Test substance"] == filter_dict["Test substance"]
    control_mask = meta["Concentration"] == 0
    mask = test_substance_mask ^ control_mask
    for key, value in filter_dict.items():
        if key not in ["Test substance", "N/A"]:
            additional_mask = meta[key] == value
            mask = mask & additional_mask
    df = meta[mask]

    # Check if any data matches the filters
    if df.empty:
        error_msg = f"No data matches the filter criteria: {filter_dict}"
        raise ValueError(error_msg)

    # Apply global filters
    df = filter_percent_mapped_reads(df, config_dict["Minimum percent mapped reads"])
    df = filter_total_mapped_reads(df, config_dict["Minimum number mapped reads"])

    # Check if any data passes the global filters
    if df.empty:
        error_msg = (
            f"No data passes the global filters: "
            f"min_percent_mapped_reads={config_dict['Minimum percent mapped reads']}, "
            f"min_num_mapped_reads={config_dict['Minimum number mapped reads']}"
        )
        raise ValueError(error_msg)

    # Apply specific filters if they exist and are not null
    if (
        "Specific filters" in config_dict
        and config_dict["Specific filters"] is not None
    ):
        for key in config_dict["Specific filters"]:
            for value in config_dict["Specific filters"][key]:
                df = df[df[key] != value]

        # Check if any data passes the specific filters
        if df.empty:
            error_msg = f"No data passes the specific filters: {config_dict['Specific filters']}"
            raise ValueError(error_msg)

    # Define Stan variables
    concentration = df["Concentration"].to_numpy()
    treatment_mask = concentration > 0

    # Validate batch key exists in the data
    batch_key = config_dict["Batch key"]
    if batch_key not in df.columns:
        error_msg = f"Batch key '{batch_key}' not found in metadata columns. Available columns: {list(df.columns)}"
        raise ValueError(error_msg)

    unique_batches = list(df[batch_key].unique())
    batch_index = np.array(
        [unique_batches.index(k) + 1 for k in df[batch_key]],
        dtype="int",
    )
    n_treatment_batch = len(np.unique(batch_index[treatment_mask]))

    # Extract counts matrix
    probes = counts_table[counts_table.columns[0]].to_numpy()
    counts = counts_table[df["Sample ID"]].to_numpy().astype("int")

    # Get num mapped reads as total count, or compute from counts table if not provided
    if "Num. mapped reads" in df.columns:
        total_count = df["Num. mapped reads"].to_numpy()
    else:
        total_count = np.sum(counts, axis=0)

    # Filter probes if median or mean raw count is below
    treatment_mask = concentration > 0
    probe_to_retain_mask = np.array(
        [
            (
                np.mean(k[treatment_mask])
                > config_dict["Minimum average treatment count"]
                and np.median(k[treatment_mask])
                > config_dict["Minimum average treatment count"]
            )
            for k in counts
        ],
    )
    probes = probes[probe_to_retain_mask]
    counts = counts[probe_to_retain_mask]

    # Check if any probes pass the filters
    if len(probes) == 0:
        error_msg = (
            f"No probes pass the filtering criteria: "
            f"min_avg_treatment_count={config_dict['Minimum average treatment count']}"
        )
        raise ValueError(error_msg)

    # Write BIFROST input as dictionary and write to file
    bifrost_input = pd.Series(
        {
            "test_substance": filter_dict["Test substance"],
            "cell_type": filter_dict["Cell type"],
            "probes": probes,
            "counts": counts,
            "total_count": total_count,
            "batch_index": batch_index,
            "concentration": concentration,
            "n_treatment_batch": n_treatment_batch,
        },
    )

    s = "".join(ch for ch in filter_dict["Test substance"] if ch.isalnum())
    for key, value in filter_dict.items():
        if key not in ["Test substance", "N/A"]:
            s += f'_{"".join(ch for ch in value if ch.isalnum())}'
    file_path = Path(output_directory) / f"BIFROST_input_{s}.json"

    bifrost_input.to_json(file_path, orient="index")


def generate_bifrost_inputs(
    meta: pd.DataFrame,
    counts_table: pd.DataFrame,
    config_dict: dict[str, Any],
    output_directory: str | Path,
) -> None:
    """Generate BIFROST inputs from the provided meta DataFrame, counts DataFrame and config dict.

    Args:
        meta: Meta data DataFrame
        counts_table: Counts data DataFrame
        config_dict: Configuration dictionary
        output_directory: Directory to write output files

    """
    test_substances = config_dict["Test substances"]
    cell_types = config_dict["Cell types"]

    for test_substance in test_substances:
        if config_dict["Additional divider"] == "N/A":
            for cell_type in cell_types:
                filter_dict = {"Test substance": test_substance, "Cell type": cell_type}
                write_bifrost_input(
                    meta,
                    filter_dict,
                    counts_table,
                    config_dict,
                    output_directory,
                )
        else:
            pairs = itertools.product(
                cell_types,
                meta[config_dict["Additional divider"]].unique(),
            )
            for pair in pairs:
                filter_dict = {
                    "Test substance": test_substance,
                    "Cell type": pair[0],
                    config_dict["Additional divider"]: pair[1],
                }
                write_bifrost_input(
                    meta,
                    filter_dict,
                    counts_table,
                    config_dict,
                    output_directory,
                )
