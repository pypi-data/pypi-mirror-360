from typing import Literal
from pydantic import BaseModel, Field, HttpUrl
from sunra_apispec.base import ImageOutput


class ImageUpscalerInput(BaseModel):
    image: HttpUrl | str = Field(
      ...,
      description="Image to enhance",
      json_schema_extra={"x-sr-order": 201}
    )
    enhance_model: Literal["Standard V2", "Low Resolution V2", "CGI", "High Fidelity V2", "Text Refine"] = Field(
        "Standard V2",
        description="Model to use: Standard V2 (general purpose), Low Resolution V2 (for low-res images), CGI (for digital art), High Fidelity V2 (preserves details), Text Refine (optimized for text)",
        json_schema_extra={"x-sr-order": 301},
    )
    upscale_factor: Literal["None", "2x", "4x", "6x"] = Field(
        "None",
        description="How much to upscale the image",
        json_schema_extra={"x-sr-order": 302}
    )
    output_format: Literal["jpeg", "png"] = Field(
        "jpeg",
        description="Output format",
        json_schema_extra={"x-sr-order": 402}
    )
    subject_detecting: Literal["None", "All", "Foreground", "Background"] = Field(
        "None",
        description="Subject detection",
        json_schema_extra={"x-sr-order": 303}
    )
    face_enhancement_creativity: float = Field(
        0,
        ge=0,
        le=1,
        multiple_of=0.01,
        description="Choose the level of creativity for face enhancement from 0 to 1. Defaults to 0, and is ignored if face_enhancement is false.",
        json_schema_extra={"x-sr-order": 304},
    )
    face_enhancement_strength: float = Field(
        0.8,
        ge=0,
        le=1,
        multiple_of=0.01,
        description="Control how sharp the enhanced faces are relative to the background from 0 to 1. Defaults to 0.8, and is ignored if face_enhancement is false.",
        json_schema_extra={"x-sr-order": 305},
    )


class ImageUpscalerOutput(ImageOutput):
    output_pixel_count: int
    units_used: int
