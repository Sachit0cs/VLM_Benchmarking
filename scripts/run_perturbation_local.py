"""
Run perturbation robustness evaluation using local cached model weights.

Usage examples:
  python scripts/run_perturbation_local.py
  python scripts/run_perturbation_local.py --models clip_vit_b32 --max-samples 50
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run perturbation evaluation with local model cache")
    parser.add_argument("--cache-dir", type=Path, default=PROJECT_ROOT / ".model_cache")
    parser.add_argument("--clean-dir", type=Path, default=PROJECT_ROOT / "datasets" / "Pertubation_original")
    parser.add_argument("--perturbed-dir", type=Path, default=PROJECT_ROOT / "datasets" / "pertubation_pertubated")
    parser.add_argument("--labels", type=Path, default=PROJECT_ROOT / "datasets" / "pertubation_pertubated" / "labels.csv")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "results" / "reports" / "local_model_robustness_perturbation_stdout.json")
    parser.add_argument("--output-md", type=Path, default=PROJECT_ROOT / "results" / "reports" / "local_model_robustness_perturbation_stdout.md")
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--no-progress", action="store_true")
    args = parser.parse_args()

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "evaluator" / "local_model_robustness.py"),
        "--mode",
        "perturbation",
        "--clean-dir",
        str(args.clean_dir),
        "--perturbed-dir",
        str(args.perturbed_dir),
        "--labels",
        str(args.labels),
        "--cache-dir",
        str(args.cache_dir),
        "--output",
        str(args.output),
        "--output-md",
        str(args.output_md),
    ]

    if args.device:
        cmd.extend(["--device", args.device])
    if args.max_samples is not None:
        cmd.extend(["--max-samples", str(args.max_samples)])
    if args.models:
        cmd.append("--models")
        cmd.extend(args.models)
    if args.no_progress:
        cmd.append("--no-progress")

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=False)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
