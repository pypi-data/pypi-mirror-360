from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List, Union


class FalInput(BaseModel):
    """Input schema for Hunyuan Video Image to Video model on FAL."""
    prompt: str = Field(
        ...,
        description="The prompt to generate the video from."
    )
    image_url: str = Field(
        ...,
        description="URL of the image input."
    )
    aspect_ratio: str = Field(
        default="16:9",
        description="The aspect ratio of the video to generate."
    )
    resolution: str = Field(
        default="720p",
        description="The resolution of the video to generate."
    )
    num_frames: int = Field(
        default=129,
        description="The number of frames to generate."
    )
    seed: Optional[int] = Field(
        default=None,
        description="The seed to use for generating the video."
    )
    i2v_stability: bool = Field(
        default=False,
        description="Turning on I2V Stability reduces hallucination but also reduces motion."
    )


class File(BaseModel):
    url: str


class FalOutput(BaseModel):
    """Output schema for Hunyuan Video Image to Video model on FAL."""
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
