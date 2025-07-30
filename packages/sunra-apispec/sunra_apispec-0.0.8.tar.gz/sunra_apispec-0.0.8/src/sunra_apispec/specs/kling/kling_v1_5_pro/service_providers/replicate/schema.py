from typing import Literal, Optional
from pydantic import BaseModel, Field


class ReplicateInput(BaseModel):
    """Input model for Replicate Kling v1.5 Pro API."""
    prompt: str = Field(
        ...,
        description="Text prompt for video generation"
    )
    negative_prompt: str = Field(
        default="",
        description="Things you do not want to see in the video"
    )
    cfg_scale: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description="Flexibility in video generation; The higher the value, the lower the model's degree of flexibility, and the stronger the relevance to the user's prompt."
    )
    start_image: Optional[str] = Field(
        default=None,
        description="First frame of the video. A start or end image is required."
    )
    end_image: Optional[str] = Field(
        default=None,
        description="Last frame of the video. A start or end image is required."
    )
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field(
        default="16:9",
        description="Aspect ratio of the video. Ignored if start_image is provided."
    )
    duration: Literal[5, 10] = Field(
        default=5,
        description="Duration of the video in seconds"
    )
