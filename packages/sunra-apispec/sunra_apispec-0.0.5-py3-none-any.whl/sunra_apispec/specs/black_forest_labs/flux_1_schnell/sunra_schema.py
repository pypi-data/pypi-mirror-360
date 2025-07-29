# Schema for Text-to-Image generation
from pydantic import BaseModel, Field
from typing import Literal


class TextToImageInput(BaseModel):
    """Input model for text-to-image generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        description="Text prompt for image generation."
    )
    number_of_steps: int = Field(
        default=4,  # Reduced number_of_steps for dev version
        ge=1,
        le=4,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 201},
        description="Number of steps for the image generation process.",
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 202},
        description="Optional seed for reproducibility.",
    )
    aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"] = Field(
        "1:1",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio for the generated image."
    )
    number_of_images: int = Field(
        default=1,
        ge=1,
        le=4,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 402},
        description="Number of outputs to generate."
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        json_schema_extra={"x-sr-order": 403},
        description="Output format for the generated image. Can be 'jpeg', 'png'"
    )
