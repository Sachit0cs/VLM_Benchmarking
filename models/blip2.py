"""
BLIP-2 Model wrapper for VLM-ARB.

BLIP-2 is a lightweight open-source Vision-Language Model from Salesforce.
Runs on HuggingFace transformers library (suitable for Colab T4 GPU).

Implementation Status: TODO
Assigned To: [Team Member Name]
"""

from PIL.Image import Image
from typing import Optional
from .base import BaseModel


class BLIP2Model(BaseModel):
    """
    BLIP-2 Vision-Language Model via HuggingFace.
    
    This is a lightweight, open-source model suitable for GPU-constrained environments.
    Requires GPU for reasonable inference speed (tested on Colab T4).
    
    Parameters:
    -----------
    precision : str, optional
        Model precision: "fp32" (full), "fp16" (half), or "int8" (quantized, default: "fp16")
    device : str, optional
        Device to load model on: "cuda" or "cpu" (default: auto-detect)
    """
    
    def __init__(self, precision: str = "fp16",
                 device: Optional[str] = None, **kwargs):
        """Initialize BLIP-2 model wrapper."""
        super().__init__(
            model_name="BLIP-2",
            model_id="blip2",
            **kwargs
        )
        self.precision = precision
        self.device = device
        self.processor = None
        self.model = None
    
    def query(self, image: Image, prompt: str) -> str:
        """
        Query BLIP-2 model with an image and prompt.
        
        Args:
            image: PIL Image to analyze
            prompt: Text prompt to send to the model
        
        Returns:
            Text response from BLIP-2
        
        TODO:
        -----
        1. Lazy-initialize model on first call:
           - Use transformers.AutoProcessor and AutoModelForVisionToSeq
           - Model ID: "Salesforce/blip2-opt-6.7b" (or -3.5b for lighter version)
           - Load with specified precision (fp16/fp32/int8)
           - Move to specified device
        2. Process image with processor
        3. Generate caption or answer based on prompt:
           - If prompt is a question: use generate() with max_length for answer
           - If prompt is empty: use generate() for captioning
        4. Decode and return the text
        5. Handle errors: OOM, missing model weights
        
        Dependencies:
        - transformers >= 4.25
        - torch with CUDA support for GPU inference
        - bitsandbytes for int8 quantization (optional)
        
        Example:
        --------
        from transformers import AutoProcessor, AutoModelForVisionToSeq
        processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-6.7b")
        model = AutoModelForVisionToSeq.from_pretrained(...)
        inputs = processor(images=image, text=prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=50)
        return processor.batch_decode(outputs)[0]
        """
        raise NotImplementedError("BLIP2Model.query() not yet implemented")
