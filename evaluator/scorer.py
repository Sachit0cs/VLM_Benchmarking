"""
Scoring and aggregation logic for evaluator.

Combines metrics into structured result objects and model-level scores.
Integrates with Firebase Firestore for cloud logging of evaluation results.

Implementation Status: Partial (core classes + cloud logging hooks)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

# Optional Firebase integration
try:
    from utilities.cloud_sync import FirebaseSync, FirestoreMetricsLogger
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


@dataclass
class AttackResult:
    """
    Result of a single attack on a single image with a single model.
    
    Attributes:
    -----------
    model_id : str
        Model identifier (e.g., "gpt4v", "blip2")
    attack_type : str
        Attack name (e.g., "typographic", "perturbation")
    image_id : str
        Image identifier from dataset
    clean_output : str
        Model output on clean (unattacked) image
    attacked_output : str
        Model output on attacked image
    attack_success_rate : float
        ASR for this specific attack (0-1)
    output_deviation_score : float
        ODS for this attack (0-1)
    cross_modal_conflict_score : float, optional
        CMCS if applicable (0-1)
    safety_bypass_rate : float, optional
        SBR if applicable (0-1)
    metadata : Dict[str, Any], optional
        Additional attack-specific info (perturbation epsilon, patch size, etc.)
    """
    model_id: str
    attack_type: str
    image_id: str
    clean_output: str
    attacked_output: str
    attack_success_rate: float
    output_deviation_score: float
    cross_modal_conflict_score: float = None
    safety_bypass_rate: float = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ModelRobustnessScore:
    """
    Aggregated robustness metrics for a single model.
    
    Computed by averaging metrics across all attacks and images.
    
    Attributes:
    -----------
    model_id : str
        Model identifier
    model_name : str
        Model human-readable name
    avg_asr : float
        Average Attack Success Rate across all attacks
    avg_ods : float
        Average Output Deviation Score
    avg_cmcs : float, optional
        Average Cross-Modal Conflict Score
    avg_sbr : float, optional
        Average Safety Bypass Rate
    composite_robustness_score : float
        Weighted aggregate robustness score
    num_attacks : int
        Total number of attacks evaluated
    num_images : int
        Number of unique images tested
    """
    model_id: str
    model_name: str
    avg_asr: float
    avg_ods: float
    composite_robustness_score: float
    num_attacks: int
    num_images: int
    avg_cmcs: float = None
    avg_sbr: float = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


def aggregate_attack_results(attack_results: List[AttackResult]) -> Dict[str, ModelRobustnessScore]:
    """
    Aggregate individual attack results into model-level robustness scores.
    
    Args:
        attack_results: List of AttackResult objects from benchmark run
    
    Returns:
        Dict mapping model_id to ModelRobustnessScore
    
    TODO:
    -----
    1. Group attack_results by model_id
    2. For each model:
       - Compute average ASR, ODS, CMCS, SBR across all attacks
       - Count unique attacks and unique images
       - Calculate composite robustness score
       - Create ModelRobustnessScore object
    3. Return dict of model_id -> score
    """
    raise NotImplementedError("aggregate_attack_results() not yet implemented")


def rank_models_by_robustness(model_scores: Dict[str, ModelRobustnessScore]) -> List[tuple]:
    """
    Rank models by overall robustness.
    
    Args:
        model_scores: Dict from aggregate_attack_results()
    
    Returns:
        List of (model_id, robustness_score) tuples sorted by robustness (best first)
    
    TODO:
    -----
    1. Extract composite_robustness_score for each model
    2. Sort by score (ascending, lower = more robust)
    3. Return list of (model_id, score) tuples
    """
    raise NotImplementedError("rank_models_by_robustness() not yet implemented")


# ====== CLOUD LOGGING HOOKS ======

def log_results_to_firestore(
    firestore_sync: 'FirebaseSync',
    run_id: str,
    model_scores: Dict[str, ModelRobustnessScore],
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Upload evaluation results to Firestore for team access.
    
    Args:
        firestore_sync: FirebaseSync instance (initialized with credentials)
        run_id: Unique run identifier
        model_scores: Model robustness scores from aggregate_attack_results()
        metadata: Additional metadata (dataset version, timestamp, etc.)
    
    Returns:
        True if successful, False otherwise
    
    Example:
        >>> from utilities.cloud_sync import FirebaseSync
        >>> fs = FirebaseSync("path/to/credentials.json")
        >>> success = log_results_to_firestore(fs, "eval_run_123", model_scores)
    """
    if not FIREBASE_AVAILABLE:
        logger.warning("Firebase not available - skipping cloud logging")
        return False
    
    try:
        # Convert dataclass objects to dicts
        metrics_dict = {
            model_id: {
                'avg_asr': score.avg_asr,
                'avg_ods': score.avg_ods,
                'avg_sbr': score.avg_sbr,
                'avg_cmcs': score.avg_cmcs,
                'composite_robustness_score': score.composite_robustness_score,
                'num_attacks': score.num_attacks,
                'num_images': score.num_images,
            }
            for model_id, score in model_scores.items()
        }
        
        # Add summary stats
        summary = {
            'total_models': len(model_scores),
            'best_model': min(model_scores.items(), 
                            key=lambda x: x[1].composite_robustness_score)[0] 
                         if model_scores else None,
            'worst_model': max(model_scores.items(),
                             key=lambda x: x[1].composite_robustness_score)[0]
                          if model_scores else None,
        }
        
        # Upload to Firestore
        firestore_sync.upload_results(
            run_id=run_id,
            metrics_dict=metrics_dict,
            metadata=metadata or {},
            collection="results"
        )
        
        logger.info(f"✅ Results logged to Firestore: {run_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to log results to Firestore: {e}")
        return False


def create_metrics_logger(
    firestore_sync: Optional['FirebaseSync'],
    run_id: str
) -> Optional['FirestoreMetricsLogger']:
    """
    Create a metrics logger for streaming results during evaluation.
    
    Useful for real-time monitoring of long-running evaluations.
    
    Args:
        firestore_sync: FirebaseSync instance (or None for offline mode)
        run_id: Unique run identifier
    
    Returns:
        FirestoreMetricsLogger instance, or None if Firebase unavailable
    
    Example:
        >>> logger = create_metrics_logger(fs, "eval_123")
        >>> logger.log_model_metrics("clip", asr=0.42, ods=0.38, sbr=0.15)
        >>> logger.flush()  # Upload all metrics
    """
    if not FIREBASE_AVAILABLE or not firestore_sync:
        return None
    
    try:
        return FirestoreMetricsLogger(firestore_sync, run_id)
    except Exception as e:
        logger.warning(f"Could not create metrics logger: {e}")
        return None

