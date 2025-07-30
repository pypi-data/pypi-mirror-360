"""
Kling Official service provider for Kling v1.6 Pro.
"""

from .adapter import KlingTextToVideoAdapter, KlingImageToVideoAdapter, KlingReferenceImagesToVideoAdapter
from .schema import KlingTextToVideoInput, KlingImageToVideoInput, KlingReferenceImagesToVideoInput

__all__ = [
    "KlingTextToVideoAdapter",
    "KlingImageToVideoAdapter", 
    "KlingReferenceImagesToVideoAdapter",
    "KlingTextToVideoInput",
    "KlingImageToVideoInput",
    "KlingReferenceImagesToVideoInput",
] 