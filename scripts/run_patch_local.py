"""Run patch robustness evaluation using the unified local evaluator."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "evaluator" / "local_model_robustness.py"),
        "--mode",
        "patch",
        "--clean-dir",
        str(PROJECT_ROOT / "datasets" / "patch_original"),
        "--perturbed-dir",
        str(PROJECT_ROOT / "datasets" / "patch_poisoned"),
        "--labels",
        str(PROJECT_ROOT / "datasets" / "patch_poisoned" / "labels.csv"),
        "--output",
        str(PROJECT_ROOT / "results" / "reports" / "local_model_robustness_patch.json"),
        "--output-md",
        str(PROJECT_ROOT / "results" / "reports" / "local_model_robustness_patch.md"),
    ]

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=False)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
