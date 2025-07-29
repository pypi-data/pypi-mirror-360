from typing import Literal
from pydantic import BaseModel, Field

from sunra_apispec.base.output_schema import VideoOutput


class TextToVideoInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt describing the desired video.",
    )

    number_of_steps: int = Field(
        default=30,
        ge=20,
        le=50,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 202},
        description="Number of sampling steps.",
    )

    # aspect_ratio: Literal["16:9", "9:16", "1:1", "custom"] = Field(
    #     default="16:9",
    #     json_schema_extra={"x-sr-order": 401},
    #     description="Aspect ratio of the output video, either '16:9', '9:16', '1:1', or 'custom'. 'custom' allows for custom width and height.",
    # )

    # resolution: Literal["480p", "720p"] = Field(
    #     default="720p",
    #     json_schema_extra={"x-sr-order": 402},
    #     description="Resolution of the output video, either '480p' or '720p'.",
    # )

    width: int = Field(
        default=864,
        ge=16,
        le=1280,
        multiple_of=16,
        json_schema_extra={"x-sr-order": 403},
        description="Custom width in pixels. Only used when aspect_ratio is 'custom'.",
    )

    height: int = Field(
        default=480,
        ge=16,
        le=1280,
        multiple_of=16,
        json_schema_extra={"x-sr-order": 404},
        description="Custom height in pixels. Only used when aspect_ratio is 'custom'.",
    )


class HunyuanVideoT2VOutput(VideoOutput):
    predict_time: float = Field(
        ...,
        description="The time taken to generate the video.",
    )
