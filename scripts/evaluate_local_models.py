"""
Compatibility wrapper for typographic local-model evaluation.

This script now delegates to evaluator/local_model_robustness.py so there is a
single source of truth for local evaluation logic.
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluator.local_model_robustness import main as unified_main


def main() -> None:
    unified_main(
        [
            "--mode",
            "typographic",
            "--mapping-csv",
            str(PROJECT_ROOT / "datasets" / "typographic_mapping.csv"),
            "--output",
            str(PROJECT_ROOT / "results" / "reports" / "local_models_typographic_report.json"),
            "--output-md",
            str(PROJECT_ROOT / "results" / "reports" / "local_models_typographic_report.md"),
        ]
    )


if __name__ == "__main__":
    main()
