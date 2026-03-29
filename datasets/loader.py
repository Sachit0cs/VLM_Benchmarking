"""
Dataset loading utilities for VLM-ARB.

Loads images and annotations from VQAv2, TextVQA, or custom datasets.

Implementation Status: TODO
Assigned To: [Team Member Name]
"""

from typing import List, Dict, Tuple, Optional
from PIL.Image import Image
from dataclasses import dataclass


@dataclass
class DataPoint:
    """
    Single datapoint from a VQA dataset.
    
    Attributes:
    -----------
    image_id : str
        Unique identifier for the image
    image : PIL.Image
        The actual image
    question : str
        Question/prompt for the image
    answers : List[str]
        Correct answers (may be multiple for VQA datasets)
    dataset_name : str
        Name of source dataset (e.g., "vqav2")
    metadata : Dict, optional
        Additional metadata (object names, scene description, etc.)
    """
    image_id: str
    image: Image
    question: str
    answers: List[str]
    dataset_name: str
    metadata: Dict = None


class DatasetLoader:
    """
    Base class for loading Vision-Language datasets.
    
    TODO: Implement dataset-specific loaders (VQAv2Loader, TextVQALoader, etc.)
    """
    
    def __init__(self, dataset_name: str, data_dir: str, **kwargs):
        """
        Initialize dataset loader.
        
        Args:
            dataset_name: Name of dataset ("vqav2", "textvqa", etc)
            data_dir: Directory containing dataset files
            **kwargs: Dataset-specific parameters
        """
        self.dataset_name = dataset_name
        self.data_dir = data_dir
        self.config = kwargs
        self.data = None
    
    def load(self, split: str = "val") -> List[DataPoint]:
        """
        Load dataset from disk.
        
        Args:
            split: Dataset split ("train", "val", "test", default: "val")
        
        Returns:
            List of DataPoint objects
        
        TODO:
        -----
        1. Check if dataset files exist in data_dir
        2. Parse annotations (JSON, CSV, etc depending on dataset)
        3. Load or reference images (may be lazy-loaded to save RAM)
        4. Create DataPoint objects with image, question, answers
        5. Return list
        
        Supported datasets:
        - VQAv2: https://visualqa.org/
        - TextVQA: https://github.com/facebookresearch/TextVQA
        - Custom: Any folder with {images/, annotations.json}
        """
        raise NotImplementedError(f"Loader for {self.dataset_name} not implemented")


def load_vqav2(data_dir: str, split: str = "val",
               annotation_file: Optional[str] = None) -> List[DataPoint]:
    """
    Load VQAv2 dataset.
    
    Args:
        data_dir: Directory containing VQA images and annotations
        split: Dataset split ("train", "val", default: "val")
        annotation_file: Path to specific annotation JSON file (if not standard)
    
    Returns:
        List of DataPoint objects from VQAv2
    
    TODO:
    -----
    1. Load annotations JSON file (e.g., mscoco_val2014_annotations.json)
    2. Parse image paths and question/answer pairs
    3. Load images from disk (or create lazy loaders)
    4. Create DataPoint for each QA pair
    5. Return list
    """
    raise NotImplementedError("load_vqav2() not yet implemented")


def load_textvqa(data_dir: str, split: str = "val") -> List[DataPoint]:
    """
    Load TextVQA dataset (contains text in images).
    
    Args:
        data_dir: Directory containing TextVQA images and annotations
        split: Dataset split ("train", "val", default: "val")
    
    Returns:
        List of DataPoint objects from TextVQA
    
    TODO:
    -----
    Implementation similar to load_vqav2 but for TextVQA format.
    TextVQA focuses on text present in images (good for testing attacks).
    """
    raise NotImplementedError("load_textvqa() not yet implemented")
