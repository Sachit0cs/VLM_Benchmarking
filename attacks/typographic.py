"""
Typographic Attack: Overlay misleading text labels on images.

This attack overlays text on images to confuse Vision-Language Models about the
actual content. For example, placing "BANANA" text over an apple image may cause
the model to output "banana" instead of "apple".

Implementation Status: COMPLETE
"""

from PIL import Image, ImageDraw, ImageFont
from .base import BaseAttack


class TypographicAttack(BaseAttack):
    """
    Typographic attack that overlays text labels on images.
    
    Parameters:
    -----------
    text_label : str
        The text to overlay on the image
    position : tuple, optional
        (x, y) position to place text (default: center)
    font_size : int, optional
        Font size in pixels (default: 40)
    font_color : tuple, optional
        RGB color tuple for text (default: (255, 0, 0) for red)
    opacity : float, optional
        Text opacity from 0.0 to 1.0 (default: 1.0)
    """
    
    def __init__(self, text_label: str, position: tuple = None, 
                 font_size: int = 40, font_color: tuple = (255, 0, 0),
                 opacity: float = 1.0, **kwargs):
        """Initialize the typographic attack."""
        super().__init__(name="Typographic", **kwargs)
        self.text_label = text_label
        self.position = position
        self.font_size = font_size
        self.font_color = font_color
        self.opacity = opacity
    
    def apply(self, image: Image, prompt: str = None) -> Image:
        """
        Apply typographic attack by overlaying text on the image.
        
        Args:
            image: PIL Image to attack
            prompt: Optional context prompt (unused for typographic attacks)
        
        Returns:
            Modified image with overlaid text
        """
        # Convert image to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Load font
        font = self._load_font()
        
        # Convert to RGBA for opacity handling
        result = image.convert('RGBA')
        
        # Create transparent text layer
        txt_layer = Image.new('RGBA', result.size, (0, 0, 0, 0))
        
        # Calculate text position
        draw_temp = ImageDraw.Draw(txt_layer)
        bbox = draw_temp.textbbox((0, 0), self.text_label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if self.position is None:
            # Center the text
            x = (result.width - text_width) // 2
            y = (result.height - text_height) // 2
        else:
            x, y = self.position
        
        # Handle opacity - convert font_color to RGBA with alpha
        alpha = int(255 * self.opacity)
        if len(self.font_color) == 3:
            font_color_with_alpha = self.font_color + (alpha,)
        else:
            font_color_with_alpha = self.font_color
        
        # Draw text on transparent layer
        draw_temp.text((x, y), self.text_label, fill=font_color_with_alpha, font=font)
        
        # Composite the text layer onto the original image
        result = Image.alpha_composite(result, txt_layer)
        
        # Convert back to RGB
        return result.convert('RGB')
    
    def _load_font(self) -> ImageFont.FreeTypeFont:
        """
        Load a font for text rendering.
        
        Attempts to load a system font; falls back to default if unavailable.
        
        Returns:
            PIL ImageFont object
        """
        # Try to load system fonts in order of preference
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, self.font_size)
            except (FileNotFoundError, OSError):
                continue
        
        # Fallback to default font if no system fonts found
        try:
            return ImageFont.load_default()
        except Exception:
            raise RuntimeError("Could not load any font. Please ensure PIL/Pillow is properly installed.")
