"""
GPT-4o Vision Model wrapper for VLM-ARB.

Connects to OpenAI's GPT-4o Vision API for querying Vision-Language capabilities.
Requires OPENAI_API_KEY in environment or .env file.

Implementation Status: TODO
Assigned To: [Team Member Name]
"""

from PIL.Image import Image
import os
from typing import Optional
from .base import BaseModel


class GPT4VisionModel(BaseModel):
    """
    GPT-4o Vision model via OpenAI API.
    
    Parameters:
    -----------
    api_key : str, optional
        OpenAI API key. If not provided, loaded from OPENAI_API_KEY env var
    max_tokens : int, optional
        Maximum tokens in response (default: 1024)
    temperature : float, optional
        Sampling temperature (default: 0.7)
    """
    
    def __init__(self, api_key: Optional[str] = None,
                 max_tokens: int = 1024, temperature: float = 0.7, **kwargs):
        """Initialize GPT-4o Vision model wrapper."""
        super().__init__(
            model_name="GPT-4 Vision",
            model_id="gpt4v",
            **kwargs
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment or constructor")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = None
    
    def query(self, image: Image, prompt: str) -> str:
        """
        Query GPT-4o Vision with an image and prompt.
        
        Args:
            image: PIL Image to analyze
            prompt: Text prompt to send to the model
        
        Returns:
            Text response from GPT-4o Vision
        
        TODO:
        -----
        1. Lazy-initialize OpenAI client on first call (using openai library)
        2. Convert PIL Image to base64 for API transmission
        3. Build the request payload with:
           - image_url or image_data (base64 encoded)
           - text prompt
           - max_tokens and temperature from self
        4. Call OpenAI API (gpt-4-vision-preview or similar model)
        5. Extract and return the text response
        6. Handle errors: quota exceeded, invalid image, API failures
        
        Dependencies:
        - openai >= 1.0 library
        - Proper API key configured
        
        Example:
        --------
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[...],
            max_tokens=self.max_tokens
        )
        """
        raise NotImplementedError("GPT4VisionModel.query() not yet implemented")
