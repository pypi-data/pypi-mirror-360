# Schema for Image-to-Image generation with Redux
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


class ImageToImageInput(BaseModel):
    """Input model for image-to-image generation with redux."""
    number_of_steps: int = Field(
        default=30,  # Reduced number_of_steps for dev version
        ge=1,
        le=50,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 201},
        description="Number of steps for the image generation process.",
    )
    guidance_scale: float = Field(
        default=3.0,
        ge=0,
        le=10,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 202},
        description="Guidance scale for image generation. High guidance_scale scales improve prompt adherence at the cost of reduced realism."
    )
    megapixels: Literal["1", "0.25"] = Field(
        default="1",
        json_schema_extra={"x-sr-order": 203},
        description="Approximate number of megapixels for generated image",
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 204},
        description="Optional seed for reproducibility.",
    )
    image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Input image to condition your output on."
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
