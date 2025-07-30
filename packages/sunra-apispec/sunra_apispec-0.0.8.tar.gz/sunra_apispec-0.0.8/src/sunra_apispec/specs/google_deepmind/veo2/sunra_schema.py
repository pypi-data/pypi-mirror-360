# Schema for Text-to-Video and Image-to-Video generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal

class TextToVideoInput(BaseModel):
    """Input model for text-to-video generation."""
    prompt: str = Field(...,
        json_schema_extra={"x-sr-order": 201},
        max_length=2500,
        description='Text prompt for video generation'
    )

    aspect_ratio: Literal['16:9', '9:16'] = Field(
        '16:9',
        json_schema_extra={"x-sr-order": 401},
        description='Aspect ratio of the video'
    )

    duration: int = Field(
        5,
        ge=5,
        le=8,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 402},
        description='Duration of the video in seconds'
    )


class ImageToVideoInput(BaseModel):
    """Input model for image-to-video generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        max_length=2500,
        description='Text prompt for video generation'
    )

    image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description='Input image to start generating from. Ideal images are 16:9 or 9:16 and 1280x720 or 720x1280, depending on the aspect ratio you choose'
    )

    aspect_ratio: Literal['16:9', '9:16'] = Field(
        '16:9',
        json_schema_extra={"x-sr-order": 401},
        description='Aspect ratio of the video'
    )

    duration: int = Field(
        5,
        ge=5,
        le=8,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 402},
        description='Duration of the video in seconds'
    )
