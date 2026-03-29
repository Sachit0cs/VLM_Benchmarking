"""
Adversarial Perturbation Attack: Add pixel-level noise using FGSM/PGD.

This attack adds imperceptible noise to images using gradient-based methods
(FGSM or PGD) to fool Vision-Language Models while remaining visually similar.

Implementation Status: TODO
Assigned To: [Team Member Name]
"""

from PIL.Image import Image
from .base import BaseAttack


class PerturbationAttack(BaseAttack):
    """
    Adversarial perturbation attack using FGSM or PGD methods.
    
    Parameters:
    -----------
    method : str
        Either "fgsm" (fast, one-step) or "pgd" (iterative, stronger)
    epsilon : float
        Maximum perturbation magnitude (typically 8/255 ≈ 0.031)
    alpha : float, optional
        Step size for PGD (default: 2/255 ≈ 0.008)
    iterations : int, optional
        Number of PGD iterations (default: 7)
    """
    
    def __init__(self, method: str = "fgsm", epsilon: float = 8/255,
                 alpha: float = 2/255, iterations: int = 7, **kwargs):
        """Initialize the perturbation attack."""
        super().__init__(name="Perturbation", **kwargs)
        if method not in ["fgsm", "pgd"]:
            raise ValueError(f"method must be 'fgsm' or 'pgd', got {method}")
        self.method = method
        self.epsilon = epsilon
        self.alpha = alpha
        self.iterations = iterations
    
    def apply(self, image: Image, prompt: str = None) -> Image:
        """
        Apply adversarial perturbation to the image.
        
        Args:
            image: PIL Image to attack
            prompt: Optional context prompt (used to generate attack target)
        
        Returns:
            Modified image with adversarial noise added
        
        TODO:
        -----
        1. Convert PIL image to tensor (normalize to [0, 1])
        2. Initialize or load a VLM model for gradient computation
        3. If method == "fgsm":
           - Compute loss gradient w.r.t. image
           - Add noise in direction of gradient (one step)
        4. If method == "pgd":
           - Loop for 'iterations' steps
           - Each step: compute gradient, add noise (step size = alpha)
           - Clip perturbation to stay within epsilon ball
        5. Clip final image to valid pixel range [0, 1] or [0, 255]
        6. Convert back to PIL Image and return
        
        Dependencies:
        - torchattacks or foolbox library
        - A loaded VLM model (pass in config or load internally)
        """
        raise NotImplementedError("PerturbationAttack.apply() not yet implemented")
