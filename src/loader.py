"""
Data loading utilities for Kalam CX.

This module is responsible for loading structured input data (JSON files)
from the data/ directory. It only handles reading and parsing raw JSON.
It does not perform validation, schema mapping, customer lookup, handbook
retrieval, transcript parsing, or any AI/decision logic.
"""

import json
import os


def load_json(path: str) -> dict:
    """Load and parse a JSON file into a Python dict.

    Args:
        path: Path to the JSON file to load.

    Returns:
        The parsed JSON content as a dictionary.

    Raises:
        FileNotFoundError: If no file exists at the given path.
        ValueError: If the file content is not valid JSON.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"JSON file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in file '{path}': {exc}") from exc
