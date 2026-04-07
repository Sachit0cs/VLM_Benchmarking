"""Adversarial patch attack and dataset generation pipeline.

This module provides:
1. `PatchAttack` for compositing a universal patch onto a single image.
2. `generate_patch_dataset` for building clean and poisoned datasets in batch.

The batch pipeline supports two input styles:
- Folder-only: recursively scans input images if no labels file is provided.
- Label-driven: consumes an existing labels.csv containing `image_file`.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image as PILImage
from PIL.Image import Image
from tqdm import tqdm

from .base import BaseAttack


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


class PatchAttack(BaseAttack):
    """
    Adversarial patch attack with a universal optimized patch.
    
    Parameters:
    -----------
    patch_size : int or tuple
        Size of the patch in pixels (e.g., 50 or (50, 50))
    patch_data : str or Image, optional
        Path to a pre-optimized patch image, or Image object. 
        If None, a random initialization is used.
    position : tuple, optional
        (x, y) position to place patch (if None, random position each time)
    opacity : float, optional
        Patch opacity from 0 to 1 (default: 1.0 for opaque)
    """
    
    def __init__(
        self,
        patch_size: int = 50,
        patch_data=None,
        position: tuple = None,
        opacity: float = 1.0,
        random_seed: Optional[int] = None,
        **kwargs,
    ):
        """Initialize the adversarial patch attack."""
        super().__init__(name="Patch", **kwargs)
        if isinstance(patch_size, int):
            self.patch_size = (patch_size, patch_size)
        else:
            self.patch_size = tuple(patch_size)

        if len(self.patch_size) != 2 or min(self.patch_size) <= 0:
            raise ValueError(f"patch_size must contain two positive values, got {self.patch_size}")

        self.patch_data = patch_data
        self.position = position
        self.opacity = max(0.0, min(1.0, float(opacity)))
        self.rng = random.Random(random_seed)
        self._patch_template = self._load_or_initialize_patch()
        self.last_patch_bbox: Optional[Tuple[int, int, int, int]] = None

    def _load_or_initialize_patch(self) -> PILImage:
        """Load user-provided patch or initialize a reusable random patch."""
        if isinstance(self.patch_data, Image):
            return self.patch_data.convert("RGBA")

        if isinstance(self.patch_data, str) and self.patch_data.strip():
            patch_path = Path(self.patch_data)
            if not patch_path.exists():
                raise FileNotFoundError(f"Patch image not found: {patch_path}")
            with PILImage.open(patch_path) as patch_obj:
                return patch_obj.convert("RGBA")

        patch_w, patch_h = self.patch_size
        noise = np.random.randint(0, 256, size=(patch_h, patch_w, 3), dtype=np.uint8)
        alpha = np.full((patch_h, patch_w, 1), 255, dtype=np.uint8)
        patch_rgba = np.concatenate([noise, alpha], axis=2)
        return PILImage.fromarray(patch_rgba, mode="RGBA")

    def _resolve_patch_position(self, image_w: int, image_h: int, patch_w: int, patch_h: int) -> Tuple[int, int]:
        """Resolve a valid top-left patch location inside the image bounds."""
        max_x = max(0, image_w - patch_w)
        max_y = max(0, image_h - patch_h)

        if self.position is None:
            return self.rng.randint(0, max_x), self.rng.randint(0, max_y)

        x, y = int(self.position[0]), int(self.position[1])
        return max(0, min(x, max_x)), max(0, min(y, max_y))
    
    def apply(self, image: Image, prompt: str = None) -> Image:
        """
        Apply adversarial patch to the image.
        
        Args:
            image: PIL Image to attack
            prompt: Optional context prompt
        
        Returns:
            Modified image with adversarial patch applied
        
        The patch attack is universal: the same patch texture is applied to each
        image, while position can be fixed or randomized.
        """
        if image.mode != "RGB":
            image = image.convert("RGB")

        base = image.convert("RGBA")
        image_w, image_h = base.size

        patch_w = min(self.patch_size[0], image_w)
        patch_h = min(self.patch_size[1], image_h)
        patch = self._patch_template.resize((patch_w, patch_h), PILImage.Resampling.BICUBIC)

        if self.opacity < 1.0:
            alpha = patch.getchannel("A")
            alpha = alpha.point(lambda p: int(p * self.opacity))
            patch.putalpha(alpha)

        x, y = self._resolve_patch_position(image_w=image_w, image_h=image_h, patch_w=patch_w, patch_h=patch_h)

        composed = base.copy()
        composed.paste(patch, (x, y), patch)
        self.last_patch_bbox = (x, y, patch_w, patch_h)
        return composed.convert("RGB")


def _read_rows_from_labels(labels_file: Path) -> List[Dict[str, str]]:
    with labels_file.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"No rows found in labels file: {labels_file}")
    if "image_file" not in rows[0]:
        raise ValueError("labels file must include an 'image_file' column")
    return rows


def _discover_rows_from_images(input_dir: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    image_paths = sorted(p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
    for path in image_paths:
        rel = str(path.relative_to(input_dir)).replace("\\", "/")
        rows.append({"image_file": rel, "label": ""})
    return rows


def _resolve_source_path(input_dir: Path, rel_image_path: str) -> Path:
    rel = rel_image_path.replace("\\", "/")
    primary = input_dir / rel
    if primary.exists():
        return primary

    fallback = input_dir / "images" / Path(rel).name
    if fallback.exists():
        return fallback

    raise FileNotFoundError(f"Image not found for row image_file={rel_image_path}")


def generate_patch_dataset(
    input_dir: Path,
    clean_output_dir: Path,
    poison_output_dir: Path,
    patch_size: int,
    patch_data: Optional[str] = None,
    position: Optional[Tuple[int, int]] = None,
    opacity: float = 1.0,
    labels_file: Optional[Path] = None,
    mapping_csv: Optional[Path] = None,
    random_seed: int = 42,
) -> Path:
    """Generate clean and patch-poisoned datasets with CSV metadata."""
    input_dir = input_dir.resolve()
    clean_output_dir = clean_output_dir.resolve()
    poison_output_dir = poison_output_dir.resolve()

    clean_output_dir.mkdir(parents=True, exist_ok=True)
    poison_output_dir.mkdir(parents=True, exist_ok=True)

    attack = PatchAttack(
        patch_size=patch_size,
        patch_data=patch_data,
        position=position,
        opacity=opacity,
        random_seed=random_seed,
    )

    rows = _read_rows_from_labels(labels_file) if labels_file and labels_file.exists() else _discover_rows_from_images(input_dir)
    if not rows:
        raise RuntimeError(f"No images found under {input_dir}")

    mapping_path = mapping_csv.resolve() if mapping_csv else (poison_output_dir / "labels.csv")
    mapping_path.parent.mkdir(parents=True, exist_ok=True)

    output_rows: List[Dict[str, str]] = []

    for row in tqdm(rows, desc="Generating patch dataset"):
        rel_image = row["image_file"].replace("\\", "/")
        src = _resolve_source_path(input_dir, rel_image)

        clean_dst = clean_output_dir / rel_image
        poison_dst = poison_output_dir / rel_image
        clean_dst.parent.mkdir(parents=True, exist_ok=True)
        poison_dst.parent.mkdir(parents=True, exist_ok=True)

        with PILImage.open(src) as img_obj:
            image = img_obj.convert("RGB")

        image.save(clean_dst)
        patched = attack.apply(image)
        patched.save(poison_dst)

        x, y, w, h = attack.last_patch_bbox or (0, 0, 0, 0)
        out_row = dict(row)
        out_row.update(
            {
                "image_file": rel_image,
                "clean_file": str(clean_dst.relative_to(clean_output_dir)).replace("\\", "/"),
                "poison_file": str(poison_dst.relative_to(poison_output_dir)).replace("\\", "/"),
                "clean_path": str(clean_dst),
                "poison_path": str(poison_dst),
                "patch_x": str(x),
                "patch_y": str(y),
                "patch_w": str(w),
                "patch_h": str(h),
                "patch_opacity": f"{opacity:.4f}",
            }
        )
        output_rows.append(out_row)

    fieldnames: List[str] = []
    for row in output_rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    with mapping_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    return mapping_path


def _parse_position(position_values: Optional[Sequence[int]]) -> Optional[Tuple[int, int]]:
    if not position_values:
        return None
    if len(position_values) != 2:
        raise ValueError("--position requires exactly 2 integers: x y")
    return int(position_values[0]), int(position_values[1])


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate clean and poisoned datasets for patch attacks")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("datasets") / "Pertubation_original",
        help="Source dataset root (supports labels-driven or folder scan mode)",
    )
    parser.add_argument(
        "--labels-file",
        type=Path,
        default=None,
        help="Optional labels CSV with image_file column; defaults to <input-dir>/labels.csv if available",
    )
    parser.add_argument(
        "--clean-output-dir",
        type=Path,
        default=Path("datasets") / "patch_original",
        help="Output directory for clean/original images",
    )
    parser.add_argument(
        "--poison-output-dir",
        type=Path,
        default=Path("datasets") / "patch_poisoned",
        help="Output directory for patch-poisoned images",
    )
    parser.add_argument(
        "--mapping-csv",
        type=Path,
        default=Path("datasets") / "patch_poisoned" / "labels.csv",
        help="CSV output path for generated metadata and paths",
    )
    parser.add_argument("--patch-size", type=int, default=64, help="Patch size in pixels")
    parser.add_argument("--patch-data", type=str, default=None, help="Optional path to custom patch image")
    parser.add_argument(
        "--position",
        type=int,
        nargs="*",
        default=None,
        help="Optional fixed patch position: x y. If omitted, random per image",
    )
    parser.add_argument("--opacity", type=float, default=1.0, help="Patch opacity in [0, 1]")
    parser.add_argument("--random-seed", type=int, default=42, help="Random seed for patch position")
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    labels_file = args.labels_file
    if labels_file is None:
        candidate = args.input_dir / "labels.csv"
        if candidate.exists():
            labels_file = candidate

    mapping_path = generate_patch_dataset(
        input_dir=args.input_dir,
        clean_output_dir=args.clean_output_dir,
        poison_output_dir=args.poison_output_dir,
        patch_size=args.patch_size,
        patch_data=args.patch_data,
        position=_parse_position(args.position),
        opacity=args.opacity,
        labels_file=labels_file,
        mapping_csv=args.mapping_csv,
        random_seed=args.random_seed,
    )
    print(f"Patch dataset generated successfully. Mapping: {mapping_path}")


if __name__ == "__main__":
    main()
