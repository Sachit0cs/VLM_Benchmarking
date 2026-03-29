"""
Abstract base class for all adversarial attacks on Vision-Language Models.

All attack implementations must inherit from BaseAttack and implement the apply() method.
"""

from abc import ABC, abstractmethod
from typing import Tuple
from PIL.Image import Image


class BaseAttack(ABC):
    """
    Abstract base class for adversarial attacks on Vision-Language Models.
    
    An attack takes an image and optional text prompt, applies perturbations or
    modifications, and returns an adversarially modified image.
    """
    
    def __init__(self, name: str, **kwargs):
        """
        Initialize the attack.
        
        Args:
            name: Human-readable name of the attack (e.g., "Typographic", "FGSM")
            **kwargs: Attack-specific hyperparameters
        """
        self.name = name
        self.config = kwargs
    
    @abstractmethod
    def apply(self, image: Image, prompt: str = None) -> Image:
        """
        Apply the adversarial attack to an image.
        
        Args:
            image: PIL Image object to attack
            prompt: Optional text prompt providing context (used by some attacks)
        
        Returns:
            PIL Image object with adversarial modifications applied
        
        Raises:
            NotImplementedError: Subclasses must implement this method
        """
        raise NotImplementedError(f"{self.name} attack must implement apply()")
    
    def __repr__(self) -> str:
        """Return string representation of the attack."""
        return f"{self.__class__.__name__}(name='{self.name}')"
