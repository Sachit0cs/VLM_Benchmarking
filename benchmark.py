"""
Main entry point for VLM-ARB benchmark.

Run the entire adversarial robustness benchmark on selected models and attacks.

Usage:
------
python benchmark.py                          # Uses config.yaml
python benchmark.py --config custom.yaml    # Uses custom config
python benchmark.py --help                  # Show all options
"""

import argparse
import logging
from typing import List, Dict, Any
from pathlib import Path
import json
from datetime import datetime
import yaml

from datasets.loader import DatasetLoader
from evaluator.metrics import attack_success_rate, output_deviation_score
from models.gpt4v import GPT4VisionModel
from models.claude import ClaudeVisionModel

# Import modules (will be implemented)
# from attacks import BaseAttack
# from models import BaseModel
# from evaluator import metrics, scorer, comparator
# from datasets import loader


logger = logging.getLogger(__name__)


class VLMArbBenchmark:
    """
    Main orchestrator for VLM-ARB adversarial robustness benchmarking.
    
    Workflow:
    1. Load config from config.yaml
    2. Initialize models and attacks
    3. Load dataset (VQAv2, TextVQA, or custom)
    4. For each model + attack combination:
       - Run attack on each image
       - Query model on clean + attacked image
       - Compute metrics
    5. Aggregate results and generate report
    
    TODO:
    -----
    Implement run() method to orchestrate full pipeline:
    - Load configuration
    - Initialize models
    - Initialize attacks
    - Load dataset
    - Run benchmarks
    - Save results
    - Generate report
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize benchmark runner.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = Path(config_path)
        self.config = None
        self.results = []
        self.timestamp = datetime.now().isoformat()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s'
        )
    
    def load_config(self) -> None:
        """
        Load configuration from YAML file.
        
        TODO:
        -----
        1. Read YAML file from self.config_path
        2. Parse models, attacks, dataset, evaluation sections
        3. Store in self.config
        4. Validate that enabled models/attacks exist
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with self.config_path.open("r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f) or {}

        if "models" not in self.config:
            self.config["models"] = []
        if "dataset" not in self.config:
            self.config["dataset"] = {"name": "typographic", "data_dir": "datasets"}
        if "output" not in self.config:
            self.config["output"] = {"save_results": True, "results_dir": "results/raw"}

    def _initialize_models(self) -> List[Any]:
        """Initialize enabled model wrappers; skip unavailable models gracefully."""
        models_cfg = self.config.get("models", [])
        initialized = []

        for model_item in models_cfg:
            if not model_item.get("enabled", False):
                continue

            name = model_item.get("name", "").lower()
            mcfg = model_item.get("config", {})
            try:
                if name == "gpt4v":
                    initialized.append(GPT4VisionModel(**mcfg))
                elif name == "claude":
                    initialized.append(ClaudeVisionModel(**mcfg))
                else:
                    logger.warning("Model '%s' is not wired in minimal benchmark path; skipping.", name)
            except Exception as exc:
                logger.warning("Skipping model '%s': %s", name, exc)

        return initialized
    
    def run(self) -> None:
        """
        Run the complete benchmark.
        
        TODO:
        -----
        1. Load configuration
        2. Initialize selected models
        3. Initialize selected attacks
        4. Load dataset
        5. For each model:
           - For each attack:
             - For each image:
               - Apply attack
               - Query model on clean image
               - Query model on attacked image
               - Compute metrics (ASR, ODS, CMCS, etc.)
               - Store AttackResult
        6. Aggregate results (ModelRobustnessScore)
        7. Save raw results to results/raw/{timestamp}.json
        8. Generate report
        """
        self.load_config()

        dataset_cfg = self.config.get("dataset", {})
        dataset_name = dataset_cfg.get("name", "typographic")
        data_dir = dataset_cfg.get("data_dir", "datasets")
        split = dataset_cfg.get("split", "val")
        sample_size = dataset_cfg.get("sample_size")
        mapping_file = dataset_cfg.get("mapping_file")

        loader = DatasetLoader(
            dataset_name=dataset_name,
            data_dir=data_dir,
            mapping_file=mapping_file,
            sample_size=sample_size,
            default_question=dataset_cfg.get("default_question", "What is in this image?"),
        )
        try:
            datapoints = loader.load(split=split)
        except NotImplementedError:
            logger.warning(
                "Dataset '%s' loader is not implemented yet. Falling back to local typographic dataset.",
                dataset_name,
            )
            fallback_loader = DatasetLoader(
                dataset_name="typographic",
                data_dir="datasets",
                sample_size=sample_size,
                default_question=dataset_cfg.get("default_question", "What is in this image?"),
            )
            datapoints = fallback_loader.load(split=split)
        if not datapoints:
            raise RuntimeError("No datapoints loaded. Check dataset configuration and files.")

        models = self._initialize_models()
        if not models:
            logger.warning("No queryable models initialized. Results will not include model outputs.")
            self.results = [
                {
                    "timestamp": self.timestamp,
                    "image_id": dp.image_id,
                    "question": dp.question,
                    "poison_text": dp.metadata.get("poison_text"),
                    "original_path": dp.metadata.get("original_path"),
                    "poison_path": dp.metadata.get("poison_path"),
                    "error": "No enabled/available model wrappers",
                }
                for dp in datapoints
            ]
            if self.config.get("output", {}).get("save_results", True):
                self.save_results()
            return

        run_results: List[Dict[str, Any]] = []
        for model in models:
            for dp in datapoints:
                poison_path = Path(dp.metadata.get("poison_path", ""))
                clean_output = ""
                attacked_output = ""
                error = None

                try:
                    clean_output = model.query(dp.image, dp.question)
                    if poison_path.exists():
                        from PIL import Image as PILImage

                        with PILImage.open(poison_path) as poison_img_obj:
                            poison_img = poison_img_obj.convert("RGB")
                        attacked_output = model.query(poison_img, dp.question)
                    else:
                        attacked_output = ""
                        error = f"Poison image missing: {poison_path}"
                except Exception as exc:
                    error = str(exc)

                asr = attack_success_rate(clean_output, attacked_output)
                ods = output_deviation_score(clean_output, attacked_output)

                run_results.append(
                    {
                        "timestamp": self.timestamp,
                        "model_id": getattr(model, "model_id", "unknown"),
                        "model_name": getattr(model, "model_name", model.__class__.__name__),
                        "image_id": dp.image_id,
                        "question": dp.question,
                        "poison_text": dp.metadata.get("poison_text"),
                        "original_path": dp.metadata.get("original_path"),
                        "poison_path": dp.metadata.get("poison_path"),
                        "clean_output": clean_output,
                        "attacked_output": attacked_output,
                        "asr": asr,
                        "ods": ods,
                        "error": error,
                    }
                )

        self.results = run_results

        if self.config.get("output", {}).get("save_results", True):
            self.save_results()
    
    def save_results(self, filepath: str = None) -> str:
        """
        Save raw results to JSON file.
        
        Args:
            filepath: Output path (default: results/raw/{timestamp}.json)
        
        Returns:
            Path to saved file
        
        TODO:
        -----
        1. Serialize self.results to list of dicts
        2. Save to JSON file
        3. Return filepath
        """
        if filepath is None:
            results_dir = Path(self.config.get("output", {}).get("results_dir", "results/raw"))
            results_dir.mkdir(parents=True, exist_ok=True)
            filepath = str(results_dir / f"{self.timestamp}.json")

        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)
        return str(output_path)
    
    def generate_report(self) -> str:
        """
        Generate final report from results.
        
        Returns:
            Path to generated report
        
        TODO:
        -----
        1. Aggregate results to ModelRobustnessScore objects
        2. Create visualizations
        3. Generate PDF/HTML report
        4. Save to results/reports/
        5. Return report path
        """
        raise NotImplementedError("generate_report() not yet implemented")


def main():
    """Parse arguments and run benchmark."""
    parser = argparse.ArgumentParser(
        description="VLM-ARB: Adversarial Robustness Benchmarking for Vision-Language Models"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Directory for saving results (default: results/)"
    )
    parser.add_argument(
        "--generate-report",
        action="store_true",
        default=True,
        help="Generate PDF/HTML report after benchmarking"
    )
    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="Skip report generation (just save raw results)"
    )
    
    args = parser.parse_args()
    
    # Initialize benchmark
    benchmark = VLMArbBenchmark(config_path=args.config)
    
    # Run benchmark
    logger.info("Starting VLM-ARB benchmark...")
    try:
        benchmark.run()
        logger.info(f"Benchmark completed. Results saved to {args.output_dir}/")
        
        # Generate report
        if not args.skip_report:
            logger.info("Generating report...")
            report_path = benchmark.generate_report()
            logger.info(f"Report generated: {report_path}")
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
