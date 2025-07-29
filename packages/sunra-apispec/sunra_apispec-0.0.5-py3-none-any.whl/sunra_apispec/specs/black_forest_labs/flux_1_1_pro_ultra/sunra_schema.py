# Schema for Text-to-Image generation with Ultra mode
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


class BaseInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        description="The prompt to use for image generation.",
    )
    prompt_enhancer: bool = Field(
        default=False,
        json_schema_extra={"x-sr-order": 201},
        description="Whether to perform enhancer on the prompt. If active, automatically modifies the prompt for more creative generation."
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 202},
        description="Seed for reproducibility.",
    )
    raw: bool = Field(
        default=False,
        json_schema_extra={"x-sr-order": 400},
        description="Generate less processed, more natural-looking images",
    )
    aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"] = Field(
        default="16:9",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the image between 21:9 and 9:21"
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        json_schema_extra={"x-sr-order": 402},
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


class TextToImageInput(BaseInput):
    """Input model for text-to-image generation with ultra mode."""
    pass


class ImageToImageInput(BaseInput):
    """Input model for image-to-image generation with ultra mode."""
    image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Image to remix"
    )
    image_strength: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 302},
        description="Blend between the prompt and the image prompt"
    )
