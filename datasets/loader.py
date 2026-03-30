"""
Dataset loading utilities for VLM-ARB.

Loads images and annotations from VQAv2, TextVQA, or custom datasets.

Implementation Status: TODO
Assigned To: [Team Member Name]
"""

from typing import List, Dict, Optional
from pathlib import Path
import csv
import json
from PIL import Image as PILImage
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
        dataset_name = self.dataset_name.lower()
        if dataset_name == "vqav2":
            return load_vqav2(self.data_dir, split=split)
        if dataset_name == "textvqa":
            return load_textvqa(self.data_dir, split=split)
        if dataset_name in {"custom", "typographic", "custom_typographic"}:
            mapping_file = self.config.get("mapping_file")
            default_question = self.config.get("default_question", "What is in this image?")
            sample_size = self.config.get("sample_size")
            datapoints = load_custom_typographic(
                data_dir=self.data_dir,
                split=split,
                mapping_file=mapping_file,
                default_question=default_question,
            )
            if isinstance(sample_size, int) and sample_size > 0:
                return datapoints[:sample_size]
            return datapoints

        raise ValueError(f"Unsupported dataset_name: {self.dataset_name}")


def load_custom_typographic(
    data_dir: str,
    split: str = "val",
    mapping_file: Optional[str] = None,
    default_question: str = "What is in this image?",
) -> List[DataPoint]:
    """
    Load local typographic benchmark dataset.

    Expected layout:
    - data_dir/typographic_original/*.jpg
    - data_dir/typographic_poison/*.jpg
    - data_dir/typographic_mapping.csv or .json (optional but recommended)
    """
    root = Path(data_dir)
    original_dir = root / "typographic_original"
    poison_dir = root / "typographic_poison"

    if not original_dir.exists():
        raise FileNotFoundError(f"Missing directory: {original_dir}")
    if not poison_dir.exists():
        raise FileNotFoundError(f"Missing directory: {poison_dir}")

    rows = []
    candidate_mappings = []
    if mapping_file:
        candidate_mappings.append(root / mapping_file)
        candidate_mappings.append(Path(mapping_file))
    candidate_mappings.extend(
        [
            root / "typographic_mapping.csv",
            root / "typographic_mapping.json",
        ]
    )

    mapping_path = next((p for p in candidate_mappings if p.exists()), None)
    if mapping_path and mapping_path.suffix.lower() == ".csv":
        with mapping_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    elif mapping_path and mapping_path.suffix.lower() == ".json":
        with mapping_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
            if isinstance(payload, list):
                rows = payload

    if not rows:
        # Fallback: derive rows from file names if mapping file is not present.
        rows = []
        for img_path in sorted(original_dir.glob("*")):
            if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            rows.append(
                {
                    "filename": img_path.name,
                    "original_path": str(original_dir / img_path.name),
                    "poison_path": str(poison_dir / img_path.name),
                    "poison_text": "",
                    "poison_exists": (poison_dir / img_path.name).exists(),
                }
            )

    datapoints: List[DataPoint] = []
    for row in rows:
        filename = row.get("filename")
        original_path = row.get("original_path") or str(original_dir / filename)
        poison_path = row.get("poison_path") or str(poison_dir / filename)
        poison_text = row.get("poison_text", "")

        orig = Path(original_path)
        if not orig.is_absolute() and not orig.exists():
            orig = root / original_path
        poi = Path(poison_path)
        if not poi.is_absolute() and not poi.exists():
            poi = root / poison_path

        if not orig.exists():
            continue

        with PILImage.open(orig) as image_obj:
            image = image_obj.convert("RGB")

        datapoints.append(
            DataPoint(
                image_id=filename or orig.stem,
                image=image,
                question=default_question,
                answers=[],
                dataset_name="custom_typographic",
                metadata={
                    "split": split,
                    "original_path": str(orig),
                    "poison_path": str(poi),
                    "poison_text": poison_text,
                    "poison_exists": poi.exists(),
                },
            )
        )

    return datapoints


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
