"""
Schema definitions for Kling Official API.
"""

from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field


class KlingBaseInput(BaseModel):
    """Base input schema for Kling generation."""
    
    model_name: Optional[str] = Field(None, description="Model name")
    prompt: Optional[str] = Field(None, max_length=2500, description="Positive text prompt")
    negative_prompt: Optional[str] = Field(None, max_length=2500, description="Negative text prompt")
    cfg_scale: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="CFG scale for guidance")
    duration: Optional[Literal["5", "10"]] = Field("5", description="Video duration in seconds")
    aspect_ratio: Optional[Literal["16:9", "9:16", "1:1"]] = Field("16:9", description="Aspect ratio")
    callback_url: Optional[str] = Field(None, description="Callback URL")
    external_task_id: Optional[str] = Field(None, description="External task ID")


class KlingTextToVideoInput(KlingBaseInput):
    """Input schema for Text-to-Video generation."""
    pass


class KlingImageToVideoInput(KlingBaseInput):
    """Input schema for Image-to-Video generation."""
    
    image: str = Field(..., description="Reference image URL or base64 encoded image")

class KlingVideoOutput(BaseModel):
    """Output schema for Kling video generation."""
    
    id: str = Field(..., description="Generated video ID")
    url: str = Field(..., description="URL for the generated video")
    duration: str = Field(..., description="Total video duration in seconds")


class KlingTaskResult(BaseModel):
    """Task result schema for Kling API response."""
    
    videos: List[KlingVideoOutput] = Field(..., description="List of generated videos")
