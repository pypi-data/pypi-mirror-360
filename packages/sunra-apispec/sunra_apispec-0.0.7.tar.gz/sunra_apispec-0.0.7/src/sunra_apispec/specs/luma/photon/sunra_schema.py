# Schema for Text-to-Image generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal

class TextToImageInput(BaseModel):
    """Input model for text-to-image generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        max_length=2500,
        description='Text prompt for image generation'
    )
    image_reference: HttpUrl | str = Field(
        None,
        json_schema_extra={"x-sr-order": 301},
        description='URL of a reference image to guide generation'
    )
    image_reference_weight: float = Field(
        default=0.85,
        json_schema_extra={"x-sr-order": 302},
        ge=0.0,
        le=1.0, 
        multiple_of=0.01,
        description='Weight of the reference image. Larger values will make the reference image have a stronger influence on the generated image.',
    )
    style_reference: HttpUrl | str = Field(
        None,
        json_schema_extra={"x-sr-order": 303},
        description='URL of a style reference image'
    )
    style_reference_weight: float = Field(
        default=0.85,
        json_schema_extra={"x-sr-order": 304},
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        description='Weight of the style reference image',
    )
    character_reference: HttpUrl | str = Field(
        None,
        json_schema_extra={"x-sr-order": 305},
        description='URL of a character reference image'
    )
    aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"] = Field(
        "16:9",
        json_schema_extra={"x-sr-order": 401},
        description='Aspect ratio of the generated image'
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 402},
        description='Random seed. Set for reproducible generation'
    )
