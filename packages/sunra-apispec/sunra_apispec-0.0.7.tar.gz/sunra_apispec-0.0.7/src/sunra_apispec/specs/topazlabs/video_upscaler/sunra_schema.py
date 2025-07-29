from typing import Literal
from pydantic import BaseModel, Field, HttpUrl
from sunra_apispec.base import VideoOutput

class VideoUpscalerInput(BaseModel):
    video: HttpUrl | str = Field(
        ...,
        description="Video file to upscale",
        json_schema_extra={"x-sr-order": 201}
    )
    target_resolution: Literal["720p", "1080p", "4k"] = Field(
        "1080p",
        description="Target resolution",
        json_schema_extra={"x-sr-order": 401}
    )
    target_fps: int = Field(
        30,
        ge=15,
        le=60,
        multiple_of=1,
        description="Target FPS (choose from 15fps to 60fps)",
        json_schema_extra={"x-sr-order": 402}
    )


class VideoUpscalerOutput(VideoOutput):
    output_pixel_count: int
    units_used: int
