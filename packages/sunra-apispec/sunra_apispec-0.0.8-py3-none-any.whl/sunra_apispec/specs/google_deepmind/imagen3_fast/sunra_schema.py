# Schema for Text-to-Image generation
from pydantic import BaseModel, Field
from typing import Literal


class TextToImageInput(BaseModel):
    """Input model for text-to-image generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        max_length=2500,
        description='The prompt for the image'
    )

    aspect_ratio: Literal['1:1', '16:9', '9:16', '4:3', '3:4'] = Field(
        '16:9',
        json_schema_extra={"x-sr-order": 401},
        description='Aspect ratio of the image'
    )
