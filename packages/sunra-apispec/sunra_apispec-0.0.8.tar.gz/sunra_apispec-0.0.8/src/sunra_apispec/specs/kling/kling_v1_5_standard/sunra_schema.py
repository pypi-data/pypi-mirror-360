# Schema for Kling v1.5-standard video generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


class BaseInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description='Text prompt for video generation'
    )
    negative_prompt: str = Field(
        None, 
        json_schema_extra={"x-sr-order": 203},
        description='Negative prompt to specify what you do not want in the generated video'
    )
    guidance_scale: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 205},
        description='Guidance scale for controlling how closely the model follows the prompt (CFG)'
    )
    duration: Literal[5, 10] = Field(
        5,
        json_schema_extra={"x-sr-order": 402},
        description='Duration of the video in seconds (5 or 10)'
    )



class ImageToVideoInput(BaseInput):
    """Input model for image-to-video generation."""
    start_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description='URL of an image file or base64 to use as the starting frame'
    )
