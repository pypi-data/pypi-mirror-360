"""
Kling Official service provider for Kling Lip Sync.
"""

from .adapter import KlingAudioLipSyncAdapter, KlingTextLipSyncAdapter
from .schema import KlingLipSyncInput

__all__ = [
    "KlingAudioLipSyncAdapter",
    "KlingTextLipSyncAdapter",
    "KlingLipSyncInput",
] 