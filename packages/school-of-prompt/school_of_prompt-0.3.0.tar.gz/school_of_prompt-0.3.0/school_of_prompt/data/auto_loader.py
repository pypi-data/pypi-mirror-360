"""
Auto data loading - smart defaults for common data formats.
Enhanced with registry support and advanced sampling strategies.
"""

import pandas as pd
from typing import Union, List, Dict, Any, Optional
from pathlib import Path

from ..core.simple_interfaces import SimpleDataSource
from .registry import get_data_registry


def auto_load_data(
    data: Union[str, pd.DataFrame, SimpleDataSource, Dict[str, str]],
    sample_size: Optional[int] = None,
    random_seed: int = 42,
    sampling_strategy: str = "random",
    enrichers: Optional[List[str]] = None,
    preprocessors: Optional[List[str]] = None
) -> Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """
    Auto-load data from various sources with smart defaults.

    Args:
        data: Path to file, DataFrame, custom data source, or dict of datasets
        sample_size: Limit to N samples (or dict with per-dataset limits)
        random_seed: Random seed for sampling
        sampling_strategy: "random", "stratified", or "balanced"
        enrichers: List of enrichment functions to apply
        preprocessors: List of preprocessing functions to apply

    Returns:
        List of dictionaries representing samples, or dict of datasets
    """
    
    # Handle multi-dataset case
    if isinstance(data, dict):
        return _load_multiple_datasets(
            data, sample_size, random_seed, sampling_strategy, enrichers, preprocessors
        )

    # Single dataset case
    if isinstance(data, SimpleDataSource):
        samples = data.load()
    elif isinstance(data, pd.DataFrame):
        samples = data.to_dict('records')
    elif isinstance(data, (str, Path)):
        samples = _load_from_file(Path(data))
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")

    # Apply preprocessing
    if preprocessors:
        samples = _apply_preprocessing(samples, preprocessors)

    # Apply enrichment
    if enrichers:
        samples = _apply_enrichment(samples, enrichers)

    # Apply sampling
    if sample_size and len(samples) > sample_size:
        samples = _apply_sampling(samples, sample_size, sampling_strategy, random_seed)

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


def _load_multiple_datasets(
    datasets: Dict[str, str],
    sample_size: Optional[Union[int, Dict[str, int]]],
    random_seed: int,
    sampling_strategy: str,
    enrichers: Optional[List[str]],
    preprocessors: Optional[List[str]]
) -> Dict[str, List[Dict[str, Any]]]:
    """Load multiple datasets."""
    result = {}
    
    for name, path in datasets.items():
        # Determine sample size for this dataset
        dataset_sample_size = None
        if isinstance(sample_size, dict):
            dataset_sample_size = sample_size.get(name)
        elif isinstance(sample_size, int):
            dataset_sample_size = sample_size
        
        # Load individual dataset
        dataset = auto_load_data(
            data=path,
            sample_size=dataset_sample_size,
            random_seed=random_seed,
            sampling_strategy=sampling_strategy,
            enrichers=enrichers,
            preprocessors=preprocessors
        )
        
        result[name] = dataset
    
    return result


def _apply_preprocessing(data: List[Dict[str, Any]], preprocessors: List[str]) -> List[Dict[str, Any]]:
    """Apply preprocessing pipeline to data."""
    registry = get_data_registry()
    pipeline = registry.get_preprocessing_pipeline(preprocessors)
    return pipeline(data)


def _apply_enrichment(data: List[Dict[str, Any]], enrichers: List[str]) -> List[Dict[str, Any]]:
    """Apply enrichment pipeline to data."""
    registry = get_data_registry()
    pipeline = registry.get_enrichment_pipeline(enrichers)
    return pipeline(data)


def _apply_sampling(
    data: List[Dict[str, Any]], 
    sample_size: int, 
    strategy: str, 
    random_seed: int
) -> List[Dict[str, Any]]:
    """Apply sampling strategy to data."""
    import random
    random.seed(random_seed)
    
    if len(data) <= sample_size:
        return data
    
    if strategy == "random":
        return random.sample(data, sample_size)
    
    elif strategy == "stratified":
        return _stratified_sample(data, sample_size)
    
    elif strategy == "balanced":
        return _balanced_sample(data, sample_size)
    
    else:
        raise ValueError(f"Unknown sampling strategy: {strategy}")


def _stratified_sample(data: List[Dict[str, Any]], sample_size: int) -> List[Dict[str, Any]]:
    """Perform stratified sampling based on label distribution."""
    # Find label field
    label_field = None
    for field in ['label', 'target', 'class', 'sentiment']:
        if field in data[0] if data else {}:
            label_field = field
            break
    
    if not label_field:
        # Fallback to random sampling if no label field
        import random
        return random.sample(data, sample_size)
    
    # Group by label
    label_groups = {}
    for item in data:
        label = item[label_field]
        if label not in label_groups:
            label_groups[label] = []
        label_groups[label].append(item)
    
    # Calculate samples per group (proportional to original distribution)
    total_samples = len(data)
    sampled_data = []
    
    for label, group in label_groups.items():
        group_proportion = len(group) / total_samples
        group_sample_size = max(1, int(sample_size * group_proportion))
        
        if len(group) <= group_sample_size:
            sampled_data.extend(group)
        else:
            import random
            sampled_data.extend(random.sample(group, group_sample_size))
    
    # If we don't have enough samples, fill randomly
    if len(sampled_data) < sample_size:
        remaining_data = [item for item in data if item not in sampled_data]
        if remaining_data:
            import random
            additional_samples = min(len(remaining_data), sample_size - len(sampled_data))
            sampled_data.extend(random.sample(remaining_data, additional_samples))
    
    # If we have too many samples, trim randomly
    if len(sampled_data) > sample_size:
        import random
        sampled_data = random.sample(sampled_data, sample_size)
    
    return sampled_data


def _balanced_sample(data: List[Dict[str, Any]], sample_size: int) -> List[Dict[str, Any]]:
    """Perform balanced sampling (equal samples per class)."""
    # Find label field
    label_field = None
    for field in ['label', 'target', 'class', 'sentiment']:
        if field in data[0] if data else {}:
            label_field = field
            break
    
    if not label_field:
        # Fallback to random sampling if no label field
        import random
        return random.sample(data, sample_size)
    
    # Group by label
    label_groups = {}
    for item in data:
        label = item[label_field]
        if label not in label_groups:
            label_groups[label] = []
        label_groups[label].append(item)
    
    # Calculate samples per group (equal distribution)
    num_groups = len(label_groups)
    samples_per_group = sample_size // num_groups
    
    sampled_data = []
    for group in label_groups.values():
        if len(group) <= samples_per_group:
            sampled_data.extend(group)
        else:
            import random
            sampled_data.extend(random.sample(group, samples_per_group))
    
    # Fill remaining slots randomly if needed
    remaining_slots = sample_size - len(sampled_data)
    if remaining_slots > 0:
        remaining_data = [item for item in data if item not in sampled_data]
        if remaining_data:
            import random
            additional_samples = min(len(remaining_data), remaining_slots)
            sampled_data.extend(random.sample(remaining_data, additional_samples))
    
    return sampled_data


# Registry integration functions
def register_custom_source(name: str, source_class: type) -> None:
    """Register a custom data source."""
    registry = get_data_registry()
    registry.register_source(name, source_class)


def register_custom_enricher(name: str, enricher_func: callable) -> None:
    """Register a custom enrichment function."""
    registry = get_data_registry()
    registry.register_enricher(name, enricher_func)


def register_custom_preprocessor(name: str, preprocessor_func: callable) -> None:
    """Register a custom preprocessing function."""
    registry = get_data_registry()
    registry.register_preprocessor(name, preprocessor_func)


def list_available_sources() -> List[str]:
    """List all available data sources."""
    registry = get_data_registry()
    return registry.list_sources()


def list_available_enrichers() -> List[str]:
    """List all available enrichment functions."""
    registry = get_data_registry()
    return registry.list_enrichers()


def list_available_preprocessors() -> List[str]:
    """List all available preprocessing functions."""
    registry = get_data_registry()
    return registry.list_preprocessors()
