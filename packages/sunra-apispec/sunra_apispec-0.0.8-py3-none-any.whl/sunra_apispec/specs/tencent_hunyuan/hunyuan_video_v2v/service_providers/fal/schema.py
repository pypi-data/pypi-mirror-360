from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List, Union


class FalInput(BaseModel):
    """Input schema for Hunyuan Video Video to Video model on FAL."""
    prompt: str = Field(
        ...,
        description="The prompt to generate the video from."
    )
    video_url: str = Field(
        ...,
        description="URL of the video input."
    )
    aspect_ratio: str = Field(
        default="16:9",
        description="The aspect ratio of the video to generate."
    )
    resolution: str = Field(
        default="720p",
        description="The resolution of the video to generate."
    )
    strength: float = Field(
        default=0.85,
        description="Strength for Video-to-Video",
        ge=0.01,
        le=1.0
    )
    enable_safety_checker: bool = Field(
        default=False,
        description="If set to true, the safety checker will be enabled."
    )


class File(BaseModel):
    url: str


class FalOutput(BaseModel):
    """Output schema for Hunyuan Video Video to Video model on FAL."""
    seed: int = Field(
        ...,
        description="The seed used for generating the video."
    )
    video: File = Field(
        ...,
        description="The generated video file."
    )


class QueueStatus(BaseModel):
    """Status schema for FAL queue."""
    status: str
    request_id: str
    response_url: Optional[str] = None
    status_url: Optional[str] = None
    cancel_url: Optional[str] = None
    logs: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    queue_position: Optional[int] = None
