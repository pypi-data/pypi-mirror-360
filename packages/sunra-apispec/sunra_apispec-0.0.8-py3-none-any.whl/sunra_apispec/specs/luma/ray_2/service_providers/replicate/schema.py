from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class Ray2BaseInput(BaseModel):
    """Base input model for Replicate Ray 2 model."""
    prompt: str = Field(
        ...,
        description="Text prompt for video generation"
    )
    start_image_url: Optional[str] = Field(
        None,
        description="URL of an image to use as the starting frame"
    )
    end_image_url: Optional[str] = Field(
        None,
        description="URL of an image to use as the ending frame"
    )
    duration: Literal[5, 9] = Field(
        5,
        description="Duration of the video in seconds"
    )
    aspect_ratio: Literal["1:1", "3:4", "4:3", "9:16", "16:9", "9:21", "21:9"] = Field(
        "16:9",
        description="Aspect ratio of the generated video"
    )
    loop: bool = Field(
        False,
        description="Whether the video should loop, with the last frame matching the first frame for smooth, continuous playback"
    )
    concepts: Optional[List[str]] = Field(
        None,
        description="List of camera concepts to apply to the video generation"
    )


class Ray2540PInput(Ray2BaseInput):
    """Input model for Replicate Ray 2 540P model."""
    pass


class Ray2720PInput(Ray2BaseInput):
    """Input model for Replicate Ray 2 720P model."""
    pass

