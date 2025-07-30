# Schema for Text-to-Image generation
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl

class TextToImageInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        max_length=2500,
        description="The prompt for the video"
    )
    prompt_enhancer: bool = Field(
        True,
        json_schema_extra={"x-sr-order": 201},
        description="Whether to use the model's prompt optimizer"
    )
    number_of_images: int = Field(
        default=4,
        ge=1,
        le=9,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 202},
        description="Number of images to generate, default is 4"
    )
    subject_reference: HttpUrl | str = Field(
        None,
        json_schema_extra={"x-sr-order": 301},
        description="URL of the subject reference image"
    )
    aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2", "21:9"] = Field(
        "1:1",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the image"
    )
