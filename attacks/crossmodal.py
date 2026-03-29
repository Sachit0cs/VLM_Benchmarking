"""
Cross-Modal Conflict Attack: Novel contribution for VLM-ARB.

This attack evaluates how Vision-Language Models respond to conflicting
information between image and text modalities. It measures modality dominance
using the novel Cross-Modal Conflict Score (CMCS).

This is NOT a traditional attack that modifies images, but rather a dataset
construction methodology to measure model robustness to modality conflicts.

Implementation Status: TODO
Assigned To: [Team Member Name]
"""

from PIL.Image import Image
from .base import BaseAttack


class CrossModalConflictAttack(BaseAttack):
    """
    Cross-modal conflict attack (dataset-based, not image modification).
    
    This attack doesn't modify the image; instead, it creates contradictory
    image+text pairs to measure which modality the VLM trusts more.
    
    Parameters:
    -----------
    conflict_type : str
        Type of conflict: "semantic" (fire + "calm beach") or "object" (dog + "cat description")
    conflict_strength : float, optional
        Strength of conflict on scale 0-1 (default: 1.0 for maximum)
    """
    
    def __init__(self, conflict_type: str = "semantic",
                 conflict_strength: float = 1.0, **kwargs):
        """Initialize the cross-modal conflict attack."""
        super().__init__(name="CrossModalConflict", **kwargs)
        if conflict_type not in ["semantic", "object"]:
            raise ValueError(f"conflict_type must be 'semantic' or 'object', got {conflict_type}")
        self.conflict_type = conflict_type
        self.conflict_strength = conflict_strength
    
    def apply(self, image: Image, prompt: str = None) -> Image:
        """
        Apply cross-modal conflict (for this attack, image is NOT modified).
        
        Args:
            image: PIL Image (unchanged by this attack)
            prompt: Original text prompt describing the actual image
        
        Returns:
            The same image (unmodified). Conflict is introduced via prompts,
            not image modifications. See generate_conflicting_prompt().
        
        Note:
        -----
        This attack operates differently from image-based attacks:
        1. The image is not modified
        2. Instead, conflicting text prompts are generated
        3. Three prompts are evaluated:
           - Prompt A: "Describe what you see" (visual)
           - Prompt B: Original prompt (may contain conflicting description)
           - Prompt C: Conflicting prompt (opposite/contradictory)
        4. CMCS metric compares outputs to measure modality dominance
        
        Implementation:
        - This method simply returns unmodified image
        - See generate_conflicting_prompt() for conflict generation
        - Evaluation happens in evaluator/metrics.py (CMCS calculation)
        """
        # For cross-modal attacks, the image is not modified
        return image
    
    def generate_conflicting_prompt(self, original_prompt: str) -> str:
        """
        Generate a conflicting text prompt opposite to the image content.
        
        Args:
            original_prompt: Original text prompt describing actual image content
        
        Returns:
            A conflicting prompt that describes something different from the image
        
        TODO:
        -----
        1. Parse the original prompt to identify the described object/scenario
        2. Generate an opposite or contradictory description
        3. Return the conflicting prompt
        
        Example:
        - Original: "Describe a peaceful beach scene"
        - Conflicting: "Describe a raging fire" (if image shows fire)
        """
        raise NotImplementedError("generate_conflicting_prompt() not yet implemented")
