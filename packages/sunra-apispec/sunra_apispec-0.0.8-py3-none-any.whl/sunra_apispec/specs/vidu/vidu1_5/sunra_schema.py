# Schema for Text-to-Image generation
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Literal


class VideoGenBaseInput(BaseModel):
    """Base class for video generation inputs"""
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 201},
        description="Random seed for generation"
    )
    duration: Literal[4, 8] = Field(
        4,
        json_schema_extra={"x-sr-order": 410},
        description="Duration of the video in seconds"
    )
    movement_amplitude: Literal["auto", "small", "medium", "large"] = Field(
        default="auto",
        json_schema_extra={"x-sr-order": 411},
        description="The movement amplitude of objects in the frame"
    )
    resolution: Literal["360p", "720p", "1080p"] = Field(
        default="720p",
        json_schema_extra={"x-sr-order": 412},
        description="Resolution of the video"
    )
  

class TextToVideoInput(VideoGenBaseInput):
    """Text to video input"""
    prompt: str = Field(
        ..., 
        json_schema_extra={"x-sr-order": 200}, 
        max_length=1500, 
        description="The prompt for the video"
    )

    style: Literal["general", "anime"] = Field(
        default="general", 
        json_schema_extra={"x-sr-order": 401}, 
        description="Style of the video"
    )

    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field(
        default="16:9",
        json_schema_extra={"x-sr-order": 402},
        description="Aspect ratio of the video"
    )


class ImageToVideoInput(VideoGenBaseInput):
    """Image to video input"""
    prompt: str = Field(
        None,
        json_schema_extra={"x-sr-order": 200},
        max_length=1500, 
        description="Optional prompt to guide the video generation"
    )

    start_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description='Start image. Required. If end_image is not provided, this image is used as a reference for image-to-video generation. If end_image is provided, this image is used as the first frame.'
    )
    
    end_image: HttpUrl | str = Field(
        None,
        json_schema_extra={"x-sr-order": 302},
        description='End image. Optional. This field is used in conjunction with start_image to define the first and last frames of the video.'
    )


class ReferenceImagesToVideoInput(VideoGenBaseInput):
    """Reference Images to video input"""

    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        max_length=1500,
        description="The prompt for the video"
    )

    reference_images: List[HttpUrl | str] = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        min_length=1,
        max_length=3,
        description="Reference images (1-3). Provide as URLs or base64 strings."
    )

    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field(
        "16:9",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the video"
    )
