import logging
from pathlib import Path
from typing import Union

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_file(file_base: Union[str, Path], filename: str) -> pd.DataFrame:
    """Load data from a CSV file and perform basic preprocessing.

    This function loads a CSV file, converts the 'Date' column to datetime if present,
    sets it as the index, and converts all columns to numeric values.

    Args:
        file_base: Base directory path
        filename: Name of the CSV file to load

    Returns:
        DataFrame containing the loaded and preprocessed data

    Raises:
        FileNotFoundError: If the file cannot be found
        ValueError: If the file cannot be parsed as a CSV
    """
    try:

        # Convert to Path object if string
        file_base = Path(file_base)

        # Get the parent directory of the file_base
        curr_dir = file_base.parent

        # Load the CSV file
        data = pd.read_csv(curr_dir / filename)

        # Convert Date column to datetime and set as index if present
        if "Date" in data.columns:
            data["Date"] = pd.to_datetime(data["Date"])
            data = data.set_index("Date")

        # Convert all columns to numeric
        for col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

        return data

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error loading file: {str(e)}")
        raise
