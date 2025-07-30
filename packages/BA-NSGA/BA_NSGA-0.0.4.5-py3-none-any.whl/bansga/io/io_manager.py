"""
io_manager.py
-------------

This module provides functions for logging and saving per-generation data
during the evolutionary optimization workflow.
"""

import os
import json
import time
import csv
import numpy as np
import logging
from typing import Optional

import yaml

class IOManager:
    """
    Handles file I/O operations: reading YAML config, exporting structures, logging, etc.
    """

    def __init__(self, base_output_path: str):
        self.base_output_path = base_output_path
        os.makedirs(self.base_output_path, exist_ok=True)
        self.logger = logging.getLogger("IOManager")
    
    def load_yaml_config(self, yaml_path: str) -> dict:
        """
        Loads a YAML configuration file and returns a dictionary of parameters.
        """
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        self.logger.info(f"Loaded configuration from {yaml_path}")
        return config

    def make_generation_dir(self, partition_label: str, generation: int) -> str:
        """
        Creates a directory for storing data associated with a specific generation.
        """
        gen_path = os.path.join(self.base_output_path, partition_label, "generation", f"gen{generation}")
        os.makedirs(gen_path, exist_ok=True)
        return gen_path

    def export_structures(self, partition, directory_path: str, label: Optional[str] = None):
        """
        Exports structures in the provided partition to the directory_path in xyz format.
        """
        os.makedirs(directory_path, exist_ok=True)
        partition.export_files(
            file_location=directory_path,
            source='xyz',
            label=label or 'enumerate',
            verbose=True
        )
        self.logger.info(f"Exported structures to {directory_path}")
    
    def save_generation_data(self, generation: int, data: dict, partition_label: str):
        """
        Saves JSON-like data into a file for record-keeping and debugging.
        """
        import json
        logger_path = os.path.join(self.base_output_path, partition_label, "logger")
        os.makedirs(logger_path, exist_ok=True)
        file_name = os.path.join(logger_path, f"generation_{generation}.json")
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=2)
        self.logger.info(f"Saved generation data to {file_name}")


def make_serializable(obj):
    """
    Recursively converts non-serializable objects to types that can be JSON-serialized.
    """
    # Convert NumPy arrays to lists.
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    # Convert NumPy scalars to native Python types.
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    # Recursively process dictionaries.
    elif isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            # Ensure keys are of valid JSON types (str, int, float, bool, or None).
            if not isinstance(key, (str, int, float, bool)) and key is not None:
                key = str(key)
            new_dict[key] = make_serializable(value)
        return new_dict
    # Process lists and tuples.
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    # If the object is already a basic type, return it as is.
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    # Fallback for other types: use string representation.
    else:
        return str(obj)

def save_generation_data(generation, data, output_directory, filename_prefix="generation_data"):
    """
    Saves per-generation data to a JSON file.

    Parameters
    ----------
    generation : int
        Current generation index.
    data : dict
        Dictionary containing information about this generation (objectives, features,
        energies, selected indices, etc.). Must be JSON-serializable.
    output_directory : str
        Path where the file will be saved.
    filename_prefix : str, optional
        Prefix for the output file name. By default 'generation_data'.

    Returns
    -------
    str
        Full path to the file that was saved.
    """
    os.makedirs(output_directory, exist_ok=True)

    # Construct a filename that includes the generation number
    filename = f"{filename_prefix}_gen{generation}.json"
    filepath = os.path.join(output_directory, filename)

    data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    serializable_data = make_serializable(data)

    # Write data to JSON
    with open(filepath, 'w') as f:
        json.dump(serializable_data, f, indent=4, sort_keys=True)

    return filepath
