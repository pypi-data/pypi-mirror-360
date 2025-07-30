# Schema for Image-to-Image generation with Canny control
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


class ImageToImageInput(BaseModel):
    """Input model for image-to-image generation with canny control."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        description="Text prompt for image generation",
    )
    number_of_steps: int = Field(
        default=30,  # Reduced number_of_steps for dev version
        ge=15,
        le=50,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 201},
        description="Number of steps for the image generation process"
    )
    guidance_scale: float = Field(
        default=30,  # Lower guidance_scale for dev version
        ge=1.0,
        le=100.0,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 202},
        description="Guidance strength for the image generation process"
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 203},
        description="Seed for reproducibility.",
    )
    control_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Image used to control the generation. The canny edge detection will be automatically generated."
    )
    number_of_images: int = Field(
        default=1,
        ge=1,
        le=4,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 401},
        description="Number of outputs to generate."
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        json_schema_extra={"x-sr-order": 402},
        description="Output format for the generated image. Can be 'jpeg' or 'png'."
    )
