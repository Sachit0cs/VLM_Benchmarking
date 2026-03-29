"""
Abstract base class for all Vision-Language Models.

All model implementations must inherit from BaseModel and implement the query() method.
"""

from abc import ABC, abstractmethod
from typing import Optional
from PIL.Image import Image


class BaseModel(ABC):
    """
    Abstract base class for Vision-Language Model wrappers.
    
    A model takes an image and text prompt, processes them through the VLM,
    and returns a text response.
    """
    
    def __init__(self, model_name: str, model_id: str, **kwargs):
        """
        Initialize the model wrapper.
        
        Args:
            model_name: Human-readable name (e.g., "GPT-4 Vision")
            model_id: Model identifier for config and logging (e.g., "gpt4v")
            **kwargs: Model-specific configuration
        """
        self.model_name = model_name
        self.model_id = model_id
        self.config = kwargs
        self._initialized = False
    
    @abstractmethod
    def query(self, image: Image, prompt: str) -> str:
        """
        Query the VLM with an image and text prompt.
        
        Args:
            image: PIL Image object to process
            prompt: Text prompt to send to the model
        
        Returns:
            Text response from the VLM
        
        Raises:
            NotImplementedError: Subclasses must implement this method
        """
        raise NotImplementedError(f"{self.model_name} must implement query()")
    
    def _initialize(self) -> None:
        """
        Lazy initialization of the model (load weights, connect to API, etc).
        
        Subclasses can override this to defer expensive setup until first query.
        """
        self._initialized = True
    
    def __repr__(self) -> str:
        """Return string representation of the model."""
        return f"{self.__class__.__name__}(model_id='{self.model_id}')"
