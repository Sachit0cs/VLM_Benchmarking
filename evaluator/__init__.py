"""
Evaluator module for VLM-ARB framework.

This package contains all evaluation metrics and scoring logic for adversarial robustness.
"""

def run_local_robustness(*args, **kwargs):
	from .local_model_robustness import run_local_robustness as _run_local_robustness

	return _run_local_robustness(*args, **kwargs)

__all__ = ["metrics", "scorer", "comparator", "run_local_robustness"]
