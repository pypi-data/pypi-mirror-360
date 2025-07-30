# Schema for VACE (Video And Content Editing) generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal, List

from sunra_apispec.base.output_schema import VideoOutput

class BaseInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt for video generation.",
    )

    number_of_steps: int = Field(
        default=50,
        ge=10,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 204},
        description="Sample steps for generation.",
    )
    
    guidance_scale: float = Field(
        default=5.0,
        ge=0,
        le=20,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 205},
        description="Sample guide scale for prompt adherence.",
    )

    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 206},
        description="Random seed for reproducibility.",
    )

    motion: Literal["consistent", "fast", "extra_fast"] = Field(
        "fast",
        json_schema_extra={"x-sr-order": 402},
        description="Speed optimization level. Faster modes may reduce quality.",
    )

    number_of_frames: int = Field(
        default=81,
        ge=81,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 404},
        description="Number of frames to generate.",
    )
    
    


class TextToVideoInput(BaseInput):
    """Input model for text-to-video generation."""
    aspect_ratio: Literal["16:9", "9:16"] = Field(
        "16:9",
        json_schema_extra={"x-sr-order": 401},
        description="Output aspect ratio.",
    )


class ImageToVideoInput(BaseInput):
    """Input model for image-to-video generation."""
    start_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Input reference images to edit. Used for image-to-video mode.",
    )

    aspect_ratio: Literal["16:9", "9:16"] = Field(
        "16:9",
        json_schema_extra={"x-sr-order": 401},
        description="Output aspect ratio.",
    )


class ReferenceImagesToVideoInput(BaseInput):
    """Input model for reference images-to-video generation."""
    reference_images: List[HttpUrl | str] = Field(
        ...,
        min_length=1,
        max_length=4,
        json_schema_extra={"x-sr-order": 301},
        description="Input reference images to edit. Used for image-to-video mode.",
    )

    aspect_ratio: Literal["16:9", "9:16"] = Field(
        "16:9",
        json_schema_extra={"x-sr-order": 401},
        description="Output aspect ratio.",
    )
    

class VideoToVideoInput(BaseInput):
    """Input model for video-to-video generation."""
    video: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Input video to edit. Required for video-to-video and inpainting modes.",
    )


class VideoInpaintingInput(BaseInput):
    """Input model for inpainting generation."""
    video: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Input video to edit. Required for video-to-video and inpainting modes.",
    )

    mask_video: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 302},
        description="Input mask video to edit. Required for inpainting mode.",
    )

class Wan21Vace13bVideoOutput(VideoOutput):
    predict_time: float = Field(
        ...,
        description="Time taken to generate the video.",
    )
