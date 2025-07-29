# Schema for Text-to-Image generation
from pydantic import BaseModel, Field
from typing import Literal

class TextToImageInput(BaseModel):
    """Input model for text-to-image generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        max_length=2500,
        description="Text prompt for image generation"
    )
    
    guidance_scale: float = Field(
        2.5,
        ge=1.0,
        le=10.0,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 201},
        description="Guidance scale for prompt adherence"
    )
    
    aspect_ratio: Literal["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3", "21:9"] = Field(
        "1:1",
        json_schema_extra={"x-sr-order": 401},
        description="Image size and aspect ratio"
    ) 

    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 404},
        description="Seed of the image generation"
    )
