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
            prompt: Text prompt to send to the model (question or empty for captioning)
        
        Returns:
            Text response from BLIP-2
        """
        import torch
        from transformers import AutoProcessor, Blip2ForConditionalGeneration
        
        # Lazy-initialize model on first call
        if self.model is None:
            # Determine device
            if self.device is None:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Model ID
            model_id = "Salesforce/blip2-opt-6.7b"
            
            # Load processor
            self.processor = AutoProcessor.from_pretrained(model_id)
            
            # Determine dtype
            if self.precision == "fp16":
                torch_dtype = torch.float16
            elif self.precision == "int8":
                torch_dtype = torch.float16  # int8 needs fp16 base
            else:
                torch_dtype = torch.float32
            
            # Load model with precision handling
            try:
                if self.precision == "int8":
                    # Int8 quantization for memory efficiency
                    self.model = Blip2ForConditionalGeneration.from_pretrained(
                        model_id,
                        torch_dtype=torch_dtype,
                        load_in_8bit=True,
                        device_map="auto"
                    )
                else:
                    # Standard loading with explicit device
                    self.model = Blip2ForConditionalGeneration.from_pretrained(
                        model_id,
                        torch_dtype=torch_dtype
                    ).to(self.device)
            except Exception as e:
                raise RuntimeError(f"Failed to load BLIP-2 model: {e}")
            
            self.model.eval()
        
        # Ensure image is RGB
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Generate text
        try:
            with torch.no_grad():
                if prompt and prompt.strip():
                    # Answer mode: use prompt as question
                    inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.device)
                    outputs = self.model.generate(**inputs, max_length=50, use_cache=True)
                else:
                    # Caption mode: generate description without prompt
                    inputs = self.processor(images=image, return_tensors="pt").to(self.device)
                    outputs = self.model.generate(**inputs, max_length=50, use_cache=True)
                
                # Decode output
                generated_text = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
                return generated_text.strip()
        except Exception as e:
            raise RuntimeError(f"BLIP-2 inference failed: {e}")
