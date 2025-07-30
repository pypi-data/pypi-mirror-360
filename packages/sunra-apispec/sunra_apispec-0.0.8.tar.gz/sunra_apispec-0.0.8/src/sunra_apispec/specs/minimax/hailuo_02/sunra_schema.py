# Schema for Text-to-Image generation
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl

class TextToVideoInput(BaseModel):
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

    resolution: Literal["768p", "1080p"] = Field(
        "1080p",
        json_schema_extra={"x-sr-order": 401},
        description="The resolution of the video, 1080p only support 6s duration"
    )

    duration: Literal[6, 10] = Field(
        6,
        json_schema_extra={"x-sr-order": 402},
        description="The duration of the video in seconds"
    )


class ImageToVideoInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        max_length=2500,
        description='The prompt for the video'
    )

    prompt_enhancer: bool = Field(True,
        json_schema_extra={"x-sr-order": 201},
        description="Whether to use the model's prompt optimizer"
    )
    
    start_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="URL of the image to use as the first frame")

    resolution: Literal["768p", "1080p"] = Field(
        "1080p",
        json_schema_extra={"x-sr-order": 401},
        description="The resolution of the video, 1080p only support 6s duration"
    )

    duration: Literal[6, 10] = Field(
        6,
        json_schema_extra={"x-sr-order": 402},
        description="The duration of the video in seconds"
    )
