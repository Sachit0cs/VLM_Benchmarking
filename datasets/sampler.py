"""
Dataset sampling utilities for VLM-ARB.

Creates balanced subsets of datasets for faster benchmarking.

Implementation Status: TODO
Assigned To: [Team Member Name]
"""

from typing import List, Optional
import random
from .loader import DataPoint


def balanced_sample(datapoints: List[DataPoint], sample_size: int,
                   balance_by: Optional[str] = None) -> List[DataPoint]:
    """
    Select a balanced subset of datapoints.
    
    Args:
        datapoints: Full dataset
        sample_size: Number of samples to select
        balance_by: Attribute to balance by (e.g., "object_type", None for random)
    
    Returns:
        Subset of datapoints (size = sample_size)
    
    TODO:
    -----
    1. If balance_by is None:
       - Randomly sample sample_size items from datapoints
    2. If balance_by is specified:
       - Group datapoints by attribute (e.g., object type)
       - Select equal number of samples from each group
       - Return balanced subset
    3. Return list of sampled DataPoints
    """
    raise NotImplementedError("balanced_sample() not yet implemented")


def stratified_sample(datapoints: List[DataPoint], test_fraction: float = 0.2,
                     random_seed: Optional[int] = None) -> tuple:
    """
    Split dataset into train/test or multiple stratified splits.
    
    Args:
        datapoints: Full dataset
        test_fraction: Fraction for test set (e.g., 0.2 for 80/20 split)
        random_seed: Seed for reproducibility (default: None)
    
    Returns:
        Tuple of (train_set, test_set) as lists
    
    TODO:
    -----
    1. Set random seed if provided
    2. Shuffle datapoints
    3. Split at test_fraction boundary
    4. Return both sets
    """
    raise NotImplementedError("stratified_sample() not yet implemented")


def subset_by_category(datapoints: List[DataPoint],
                      category: str, category_values: List[str]) -> List[DataPoint]:
    """
    Filter datapoints to only include specific categories.
    
    Args:
        datapoints: Full dataset
        category: Metadata field to filter by (e.g., "object_type")
        category_values: List of allowed values (e.g., ["dog", "cat", "bird"])
    
    Returns:
        Filtered list of datapoints
    
    TODO:
    -----
    1. Filter datapoints where metadata[category] is in category_values
    2. Return filtered list
    
    Example:
    --------
    animals = subset_by_category(data, "object_type", ["dog", "cat"])
    """
    raise NotImplementedError("subset_by_category() not yet implemented")
