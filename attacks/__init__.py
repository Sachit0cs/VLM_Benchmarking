"""
Attack modules for VLM-ARB framework.

This package contains all adversarial attack implementations for Vision-Language Models.
Each attack inherits from BaseAttack and implements the apply() method.
"""

from .base import BaseAttack
from .typographic import TypographicAttack
from .prompt_injection import PromptInjectionAttack
from .patch import PatchAttack

__all__ = ["BaseAttack", "TypographicAttack", "PromptInjectionAttack", "PatchAttack"]
