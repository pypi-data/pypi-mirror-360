# Schema for Image-to-Image generation with Depth control
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


class ImageToImageInput(BaseModel):
    """Input model for image-to-image generation with depth control."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        description="Text prompt for image generation",
    )
    prompt_enhancer: bool = Field(
        default=False,
        json_schema_extra={"x-sr-order": 201},
        description="Whether to perform enhancer on the prompt. If active, automatically modifies the prompt for more creative generation."
    )
    number_of_steps: int = Field(
        default=30,
        ge=15,
        le=50,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 202},
        description="Number of steps for the image generation process"
    )
    guidance_scale: float = Field(
        default=15,
        ge=1.0,
        le=100.0,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 203},
        description="Guidance strength for the image generation process"
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 204},
        description="Seed for reproducibility.",
    )
    control_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Input image to condition your output on."
    )
    preprocessed_image: HttpUrl | str = Field(
        default=None,
        json_schema_extra={"x-sr-order": 302},
        description="Pre-processed image that will bypass the control preprocessing step"
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        json_schema_extra={"x-sr-order": 401},
        description="Output format for the generated image. Can be 'jpeg' or 'png'."
    )
    safety_tolerance: int = Field(
        default=40,
        ge=0,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 500},
        description="Tolerance level for input and output moderation. Between 0 and 100, 0 being most strict, 100 being no moderation.",
    )
