"""
LLaVA-7B Model wrapper for VLM-ARB.

LLaVA (Large Language and Vision Assistant) is an open-source Vision-Language Model.
Runs on HuggingFace transformers library (suitable for Colab T4 GPU).

Implementation Status: TODO
Assigned To: [Team Member Name]
"""

from PIL.Image import Image
from typing import Optional
from .base import BaseModel


class LLaVAModel(BaseModel):
    """
    LLaVA-7B Vision-Language Model via HuggingFace.
    
    Open-source and multimodal model. Requires GPU for inference.
    Weights: ~14GB for 7B model (fits on Colab T4 with int8 quantization).
    
    Parameters:
    -----------
    model_id : str, optional
        HuggingFace model ID (default: "llava-hf/llava-1.5-7b-hf")
    precision : str, optional
        Model precision: "fp32", "fp16", or "int8" (default: "int8" for low memory)
    device : str, optional
        Device to load model on: "cuda" or "cpu" (default: auto-detect)
    """
    
    def __init__(self, model_id: str = "llava-hf/llava-1.5-7b-hf",
                 precision: str = "int8", device: Optional[str] = None, **kwargs):
        """Initialize LLaVA model wrapper."""
        super().__init__(
            model_name="LLaVA-7B",
            model_id="llava",
            **kwargs
        )
        self.llava_model_id = model_id
        self.precision = precision
        self.device = device
        self.processor = None
        self.model = None
    
    def query(self, image: Image, prompt: str) -> str:
        """
        Query LLaVA model with an image and prompt.
        
        Args:
            image: PIL Image to analyze
            prompt: Text prompt/question for the model
        
        Returns:
            Text response from LLaVA
        """
        import torch
        from transformers import AutoProcessor, LlavaForConditionalGeneration
        
        # Lazy-initialize model on first call
        if self.model is None:
            # Determine device
            if self.device is None:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load processor
            self.processor = AutoProcessor.from_pretrained(self.llava_model_id)
            
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
                    # Int8 quantization for memory efficiency (recommended for 7B on T4)
                    self.model = LlavaForConditionalGeneration.from_pretrained(
                        self.llava_model_id,
                        torch_dtype=torch_dtype,
                        load_in_8bit=True,
                        device_map="auto",
                        low_cpu_mem_usage=True
                    )
                else:
                    # Standard loading with explicit device
                    self.model = LlavaForConditionalGeneration.from_pretrained(
                        self.llava_model_id,
                        torch_dtype=torch_dtype,
                        low_cpu_mem_usage=True
                    ).to(self.device)
            except Exception as e:
                raise RuntimeError(f"Failed to load LLaVA model from {self.llava_model_id}: {e}")
            
            self.model.eval()
        
        # Ensure image is RGB
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Use default prompt if none provided
        if not prompt or not prompt.strip():
            prompt = "Describe this image in detail."
        
        # Generate text
        try:
            with torch.no_grad():
                # Process input (LLaVA expects specific formatting)
                inputs = self.processor(text=prompt, images=image, return_tensors="pt").to(self.device)
                
                # Generate response
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    use_cache=True,
                    temperature=0.7
                )
                
                # Decode output
                generated_text = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
                
                # Clean up the output (remove prompt if included)
                if prompt in generated_text:
                    generated_text = generated_text.replace(prompt, "").strip()
                
                return generated_text.strip()
        except Exception as e:
            raise RuntimeError(f"LLaVA inference failed: {e}")
