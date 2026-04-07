"""Generate clean and patch-poisoned datasets for patch-attack benchmarking.

Usage examples:
  python scripts/generate_patch_dataset.py
  python scripts/generate_patch_dataset.py --patch-size 80 --opacity 0.85
  python scripts/generate_patch_dataset.py --patch-data assets/patch.png --position 24 24
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from attacks.patch import generate_patch_dataset


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate patch attack datasets")
    parser.add_argument("--input-dir", type=Path, default=PROJECT_ROOT / "datasets" / "Pertubation_original")
    parser.add_argument("--labels-file", type=Path, default=None)
    parser.add_argument("--clean-output-dir", type=Path, default=PROJECT_ROOT / "datasets" / "patch_original")
    parser.add_argument("--poison-output-dir", type=Path, default=PROJECT_ROOT / "datasets" / "patch_poisoned")
    parser.add_argument(
        "--mapping-csv",
        type=Path,
        default=PROJECT_ROOT / "datasets" / "patch_poisoned" / "labels.csv",
    )
    parser.add_argument("--patch-size", type=int, default=64)
    parser.add_argument("--patch-data", type=str, default=None)
    parser.add_argument("--position", type=int, nargs="*", default=None, help="Optional x y")
    parser.add_argument("--opacity", type=float, default=1.0)
    parser.add_argument("--random-seed", type=int, default=42)
    return parser


def _parse_position(values):
    if not values:
        return None
    if len(values) != 2:
        raise ValueError("--position requires exactly 2 integers: x y")
    return int(values[0]), int(values[1])


def main() -> None:
    args = _build_parser().parse_args()

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

    print(f"Patch dataset generation complete. Mapping file: {mapping_path}")


if __name__ == "__main__":
    main()
