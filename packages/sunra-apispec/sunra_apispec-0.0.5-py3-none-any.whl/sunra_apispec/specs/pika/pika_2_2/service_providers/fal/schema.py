from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List, Literal


class PikaImage(BaseModel):
    image_url: str = Field(
        ...,
        description="URL of the image to include"
    )


class FalInput(BaseModel):
    """Input schema for Pika 2.2 Pikascenes model on FAL."""
    prompt: str = Field(
        ...,
        description="Text prompt describing the desired video"
    )
    images: List[PikaImage] = Field(
        ...,
        description="List of images to use for video generation"
    )
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:5", "5:4", "3:2", "2:3"] = Field(
        default="16:9",
        description="The aspect ratio of the generated video"
    )
    resolution: Literal["720p", "1080p"] = Field(
        default="720p",
        description="The resolution of the generated video"
    )
    duration: int = Field(
        default=5,
        description="The duration of the generated video in seconds"
    )
    ingredients_mode: Literal["creative", "precise"] = Field(
        default="creative",
        description="Mode for integrating multiple images"
    )
    seed: Optional[int] = Field(
        default=None,
        description="The seed for the random number generator"
    )
    negative_prompt: str = Field(
        default="",
        description="A negative prompt to guide the model"
    )


class File(BaseModel):
    url: str
    file_size: Optional[int] = None
    file_name: Optional[str] = None
    content_type: Optional[str] = None


class FalOutput(BaseModel):
    """Output schema for Pika 2.2 Pikascenes model on FAL."""
    video: File = Field(
        ...,
        description="The generated video"
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
