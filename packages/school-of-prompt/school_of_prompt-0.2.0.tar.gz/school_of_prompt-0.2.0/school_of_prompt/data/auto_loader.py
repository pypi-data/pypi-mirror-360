"""
Auto data loading - smart defaults for common data formats.
"""

import pandas as pd
from typing import Union, List, Dict, Any, Optional
from pathlib import Path

from ..core.simple_interfaces import SimpleDataSource


def auto_load_data(
    data: Union[str, pd.DataFrame, SimpleDataSource],
    sample_size: Optional[int] = None,
    random_seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Auto-load data from various sources with smart defaults.

    Args:
        data: Path to file, DataFrame, or custom data source
        sample_size: Limit to N samples (random sampling)
        random_seed: Random seed for sampling

    Returns:
        List of dictionaries representing samples
    """

    if isinstance(data, SimpleDataSource):
        samples = data.load()
    elif isinstance(data, pd.DataFrame):
        samples = data.to_dict('records')
    elif isinstance(data, (str, Path)):
        samples = _load_from_file(Path(data))
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")

    # Apply sampling if requested
    if sample_size and len(samples) > sample_size:
        import random
        random.seed(random_seed)
        samples = random.sample(samples, sample_size)

    return samples


def _load_from_file(path: Path) -> List[Dict[str, Any]]:
    """Load data from file with format auto-detection."""

    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    suffix = path.suffix.lower()

    if suffix == '.csv':
        return _load_csv(path)
    elif suffix in ['.jsonl', '.json']:
        return _load_jsonl(path)
    else:
        # Try to detect format from content
        with open(path, 'r') as f:
            first_line = f.readline().strip()

        if first_line.startswith('{'):
            return _load_jsonl(path)
        elif ',' in first_line:
            return _load_csv(path)
        else:
            raise ValueError(f"Cannot detect format for file: {path}")


def _load_csv(path: Path) -> List[Dict[str, Any]]:
    """Load CSV file."""
    df = pd.read_csv(path)
    return df.to_dict('records')


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load JSONL file."""
    import json

    samples = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                samples.append(json.loads(line))

    return samples
