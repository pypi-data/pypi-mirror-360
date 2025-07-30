"""
Kling Official service provider for Kling v1.5 Pro.
"""

from .adapter import KlingImageToVideoAdapter
from .schema import KlingImageToVideoInput

__all__ = [
    "KlingImageToVideoAdapter",
    "KlingImageToVideoInput",
] 