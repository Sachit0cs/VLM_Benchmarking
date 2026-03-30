"""
Visual Prompt Injection Attack: Embed hidden instructions in images.

This attack embeds hidden text instructions inside images to hijack VLM behavior
without modifying the text prompt. Implements HOUYI's 3-component structure:
1. Framework Component: Natural-looking context text
2. Separator Component: Creates context break (syntax/semantic-based)
3. Disruptor Component: The malicious instruction

Paper reference: Liu et al., "Prompt Injection Attack Against LLM-integrated Applications"
"""

import os
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont
import io
import random
from attacks.base import BaseAttack


class PromptInjectionAttack(BaseAttack):
    """
    Visual prompt injection attack with HOUYI's 3-component structure.
    
    Embeds hidden text instructions in images using multiple techniques:
    - white_on_white: White text on white background
    - low_opacity: Semi-transparent text overlay
    - steganography: LSB encoding (imperceptible)
    
    Implements HOUYI's approach: Framework → Separator → Disruptor
    """
    
    def __init__(self, 
                 injection_text: str,
                 technique: str = "white_on_white",
                 opacity: float = 0.1,
                 use_houyi_structure: bool = True,
                 separator_type: str = "syntax",
                 framework_text: Optional[str] = None,
                 position: str = "bottom_right",
                 **kwargs):
        """
        Initialize visual prompt injection attack.
        
        Args:
            injection_text: The malicious instruction to embed (Disruptor)
            technique: Embedding method ("white_on_white", "low_opacity", "steganography")
            opacity: Opacity for low_opacity method (0.0-1.0)
            use_houyi_structure: Whether to use HOUYI's 3-component structure
            separator_type: Type of separator ("syntax", "semantic", "visual_spacing")
            framework_text: Optional framework component text (auto-generated if None)
            position: Text position in image ("top_left", "bottom_right", "center", "random")
        """
        super().__init__(name="PromptInjection", **kwargs)
        
        if technique not in ["white_on_white", "low_opacity", "steganography"]:
            raise ValueError(f"technique must be one of three supported methods, got {technique}")
        if separator_type not in ["syntax", "semantic", "visual_spacing"]:
            raise ValueError(f"separator_type must be 'syntax', 'semantic', or 'visual_spacing'")
        if not (0.0 <= opacity <= 1.0):
            raise ValueError(f"opacity must be between 0.0 and 1.0, got {opacity}")
        
        self.injection_text = injection_text
        self.technique = technique
        self.opacity = opacity
        self.use_houyi_structure = use_houyi_structure
        self.separator_type = separator_type
        self.framework_text = framework_text or self._generate_framework()
        self.position = position
    
    def _generate_framework(self) -> str:
        """
        Generate framework component: Natural-looking context text.
        
        Returns:
            Framework text that blends naturally with image context.
        """
        frameworks = [
            "Image Description:\n",
            "Analysis:\n",
            "Summary:\n",
            "Below is the image analysis:\n",
            "Image caption:\n",
        ]
        return frameworks[0]  # Use first one, could be randomized
    
    def _generate_separator(self, injection_text: str) -> str:
        """
        Generate separator component: Creates context break between framework and disruptor.
        
        Args:
            injection_text: The instruction to separate from framework
        
        Returns:
            Formatted text with framework, separator, and disruptor
        """
        if self.separator_type == "syntax":
            # Syntax-based: Use escape characters and newlines
            separator = "\n" * 3 + "---" * 5 + "\n"
            return f"{self.framework_text}{separator}{injection_text}"
        
        elif self.separator_type == "semantic":
            # Semantic-based: Reasoning summary + task shift
            separator = "\nBased on the analysis above, "
            return f"{self.framework_text}{separator}{injection_text}"
        
        elif self.separator_type == "visual_spacing":
            # Visual spacing: Use whitespace/invisible characters
            separator = "\n" * 5 + " " * 50 + "\n"
            return f"{self.framework_text}{separator}{injection_text}"
        
        return f"{self.framework_text}\n{injection_text}"
    
    def apply(self, image: Image.Image, prompt: str = None) -> Image.Image:
        """
        Apply visual prompt injection by embedding hidden text in the image.
        
        Uses HOUYI's 3-component structure:
        1. Framework: Natural-looking introductory text
        2. Separator: Context break (syntax/semantic/visual)
        3. Disruptor: Malicious instruction
        
        Args:
            image: PIL Image to inject into
            prompt: Optional original user prompt (for reference)
        
        Returns:
            Modified image with hidden instruction embedded
        
        Raises:
            ValueError: If technique is not supported
        """
        # Generate complete injection text using HOUYI structure
        if self.use_houyi_structure:
            complete_text = self._generate_separator(self.injection_text)
        else:
            complete_text = self.injection_text
        
        if self.technique == "white_on_white":
            return self._embed_white_on_white(image, complete_text)
        elif self.technique == "low_opacity":
            return self._embed_low_opacity(image, complete_text)
        elif self.technique == "steganography":
            return self._embed_steganography(image, complete_text)
        else:
            raise ValueError(f"Unsupported technique: {self.technique}")
    
    def _embed_white_on_white(self, image: Image.Image, text: str) -> Image.Image:
        """
        Embed text using white-on-white technique.
        
        Args:
            image: Original PIL Image
            text: Hidden text to embed
        
        Returns:
            Image with white text on white background
        """
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Create a copy to avoid modifying original
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        # Try to load a default font, fallback to default if not available
        try:
            font_size = 8
            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
        except (IOError, OSError):
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text position
        position = self._get_text_position(image.size, text)
        
        # Draw white text on white background (visible only to VLM due to compression artifacts)
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        return img_copy
    
    def _embed_low_opacity(self, image: Image.Image, text: str) -> Image.Image:
        """
        Embed text using low-opacity overlay technique.
        
        Args:
            image: Original PIL Image
            text: Hidden text to embed
        
        Returns:
            Image with semi-transparent text overlay
        """
        # Convert to RGBA for transparency
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        else:
            image = image.copy()
        
        # Create transparent layer for text
        txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Load font
        try:
            font_size = 8
            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
        except (IOError, OSError):
            font = ImageFont.load_default()
        
        # Calculate position
        position = self._get_text_position(image.size, text)
        
        # Draw text with specified opacity
        alpha = int(255 * self.opacity)
        draw.text(position, text, fill=(0, 0, 0, alpha), font=font)
        
        # Composite text layer onto original image
        result = Image.alpha_composite(image, txt_layer)
        return result.convert("RGB") if image.mode == "RGB" else result
    
    def _embed_steganography(self, image: Image.Image, text: str) -> Image.Image:
        """
        Embed text using steganography (LSB encoding).
        
        Encodes instruction in least significant bits of pixel values.
        Most imperceptible but requires stegano library.
        
        Args:
            image: Original PIL Image
            text: Hidden text to embed
        
        Returns:
            Image with steganographically encoded text
        """
        try:
            from stegano import lsb
        except ImportError:
            print("Warning: stegano library not installed. Falling back to white-on-white.")
            return self._embed_white_on_white(image, text)
        
        # Convert image to RGB
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Encode text in LSBs
        try:
            secret = lsb.hide(image, text)
            return secret
        except Exception as e:
            print(f"Steganography encoding failed: {e}. Falling back to white-on-white.")
            return self._embed_white_on_white(image, text)
    
    def _get_text_position(self, image_size: Tuple[int, int], text: str) -> Tuple[int, int]:
        """
        Calculate text position in image.
        
        Args:
            image_size: (width, height) of image
            text: Text to position
        
        Returns:
            (x, y) coordinates for text placement
        """
        if self.position == "top_left":
            return (5, 5)
        elif self.position == "bottom_right":
            return (image_size[0] - 100, image_size[1] - 20)
        elif self.position == "center":
            return (image_size[0] // 2 - 50, image_size[1] // 2)
        else:  # "random"
            x = random.randint(5, max(5, image_size[0] - 100))
            y = random.randint(5, max(5, image_size[1] - 20))
            return (x, y)
