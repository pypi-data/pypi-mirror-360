from pydantic import BaseModel, Field
from pydantic import HttpUrl

from sunra_apispec.base.output_schema import VideoOutput

class VideoToVideoInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt describing the desired video.",
    )

    video: HttpUrl | str = Field(
        ...,
        title="Video",
        json_schema_extra={"x-sr-order": 202},
        description="Path to the video to use for video generation.",
    )


class HunyuanVideoV2VOutput(VideoOutput):
    predict_time: float = Field(
        ...,
        description="Time taken to generate the video.",
    )