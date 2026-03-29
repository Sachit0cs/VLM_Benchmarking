"""
Prompt Injection Attack: Embed hidden instructions in images.

This attack embeds hidden text instructions inside images (white text on white
background, low opacity overlays, or steganography) to hijack VLM behavior
without modifying the text prompt.

Implementation Status: TODO
Assigned To: [Team Member Name]
"""

from PIL.Image import Image
from .base import BaseAttack


class PromptInjectionAttack(BaseAttack):
    """
    Prompt injection attack that embeds hidden text in images.
    
    Parameters:
    -----------
    injection_text : str
        The hidden instruction to embed in the image
    technique : str
        Embedding technique: "white_on_white", "low_opacity", or "steganography"
    opacity : float, optional
        Opacity level for low_opacity technique (default: 0.1)
    """
    
    def __init__(self, injection_text: str, technique: str = "white_on_white",
                 opacity: float = 0.1, **kwargs):
        """Initialize the prompt injection attack."""
        super().__init__(name="PromptInjection", **kwargs)
        if technique not in ["white_on_white", "low_opacity", "steganography"]:
            raise ValueError(f"technique must be one of the three supported methods, got {technique}")
        self.injection_text = injection_text
        self.technique = technique
        self.opacity = opacity
    
    def apply(self, image: Image, prompt: str = None) -> Image:
        """
        Apply prompt injection by embedding hidden text in the image.
        
        Args:
            image: PIL Image to inject into
            prompt: Optional original prompt (for reference)
        
        Returns:
            Modified image with hidden instruction embedded
        
        TODO:
        -----
        1. If technique == "white_on_white":
           - Use PIL to draw white text on white background
           - Position text somewhere in the image (corner or center)
        2. If technique == "low_opacity":
           - Create a semi-transparent text layer
           - Overlay it on the image with reduced opacity
        3. If technique == "steganography":
           - Embed text in LSBs or use stegano library
           - Hide instruction imperceptibly in pixel data
        4. Return the modified image
        
        Dependencies:
        - Pillow for text rendering
        - stegano library for steganography option
        """
        raise NotImplementedError("PromptInjectionAttack.apply() not yet implemented")
