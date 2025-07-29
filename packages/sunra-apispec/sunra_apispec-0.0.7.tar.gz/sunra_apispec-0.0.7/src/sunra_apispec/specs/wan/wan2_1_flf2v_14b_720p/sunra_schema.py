# Schema for FLF2V (First-Last-Frame to Video) generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal

class ImageToVideoInput(BaseModel):
    """Input model for Image to Video generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="The text prompt to guide video generation.",
    )

    prompt_enhancer: bool = Field(
        True,
        json_schema_extra={"x-sr-order": 202},
        description="Whether to use the prompt enhancer.",
    )
    
    number_of_steps: int = Field(
        default=30,
        ge=2,
        le=40,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 204},
        description="Number of inference steps for sampling. Higher values give better quality but take longer.",
    )
    
    guidance_scale: float = Field(
        default=5.0,
        ge=1.0,
        le=10.0,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 205},
        description="Classifier-free guidance scale. Higher values give better adherence to the prompt but may decrease quality.",
    )
    
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 206},
        description="Random seed for reproducibility.",
    )
    
    start_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="URL of the starting image. If the input image does not match the chosen aspect ratio, it is resized and center cropped.",
    )
    
    end_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 302},
        description="URL of the ending image. If the input image does not match the chosen aspect ratio, it is resized and center cropped.",
    )
    
    resolution: Literal["480p", "720p"] = Field(
        "720p",
        json_schema_extra={"x-sr-order": 403},
        description="Resolution of the generated video (480p or 720p).",
    )
    
    aspect_ratio: Literal["auto", "16:9", "9:16", "1:1"] = Field(
        "auto",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the generated video. If 'auto', the aspect ratio will be determined automatically based on the input image.",
    )
    
    number_of_frames: int = Field(
        default=81,
        ge=81,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 404},
        description="Number of frames to generate. Must be between 81 to 100 (inclusive).",
    )
    
    frames_per_second: int = Field(
        default=16,
        ge=5,
        le=24,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 405},
        description="Frames per second of the generated video. Must be between 5 to 24.",
    )
    
    acceleration: Literal["none", "regular"] = Field(
        default="regular",
        json_schema_extra={"x-sr-order": 501},
        description="Acceleration level to use. The more acceleration, the faster the generation, but with lower quality.",
    )
