"""
Attack modules for VLM-ARB framework.

This package contains all adversarial attack implementations for Vision-Language Models.
Each attack inherits from BaseAttack and implements the apply() method.
"""

from .base import BaseAttack
from .prompt_injection import PromptInjectionAttack

__all__ = ["BaseAttack", "PromptInjectionAttack"]
