# Schema for Text-to-Image generation
from pydantic import BaseModel, Field
from typing import Literal

from sunra_apispec.base.output_schema import ImageOutput


class TextToImageInput(BaseModel):
    """Text to image input for HiDream I1 Dev model"""

    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt for image generation"
    )
    
    negative_prompt: str = Field(
        None,
        json_schema_extra={"x-sr-order": 203},
        description="Negative prompt to avoid certain elements"
    )
    
    aspect_ratio: Literal["1:1", "2:3", "3:4", "9:16", "3:2", "4:3", "16:9"] = Field(
        "1:1",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the generated image"
    )
    
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 206},
        description="Random seed for generation"
    )


class HiDreamI1DevOutput(ImageOutput):
    predict_time: float = Field(
        ...,
        description="Time taken to generate the image",
    )

