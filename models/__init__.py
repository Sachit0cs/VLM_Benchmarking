"""
Model modules for VLM-ARB framework.

This package contains all Vision-Language Model implementations for querying.
Each model inherits from BaseModel and implements the query() method.
"""

from .base import BaseModel

__all__ = ["BaseModel"]
