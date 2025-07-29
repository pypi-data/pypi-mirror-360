from pydantic import BaseModel, Field, HttpUrl
from typing import Literal
from sunra_apispec.base.output_schema import VideoOutput, SunraFile


class TextToVideoInput(BaseModel):
    """Input model for text-to-video generation using LTX Video 0.9.7."""
    
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        min_length=1,
        max_length=32000,
        description="Text description of the desired video."
    )
    
    resolution: Literal["480p", "720p"] = Field(
        "720p",
        json_schema_extra={"x-sr-order": 401},
        description="Output video resolution. 720p (default) or 480p."
    )
    
    aspect_ratio: Literal["1:1", "16:9", "9:16"] = Field(
        "1:1",
        json_schema_extra={"x-sr-order": 402},
        description="Aspect ratio of the generated video. 720p: 1024x1024 (1:1), 1280x720 (16:9), 720x1280 (9:16). 480p: 640x640 (1:1), 864x480 (16:9), 480x864 (9:16)."
    )
    
    number_of_frames: int = Field(
        161,
        json_schema_extra={"x-sr-order": 403},
        description="The number of frame count will be 8N+1 (e.g., 9, 17, 25, 161). Default: 161"
    )
    
    frames_per_second: int = Field(
        24,
        json_schema_extra={"x-sr-order": 404},
        description="Frames per second for the output video. Default: 24"
    )


class ImageToVideoInput(BaseModel):
    """Input model for image-to-video generation using LTX Video 0.9.7."""
    
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        min_length=1,
        max_length=32000,
        description="Text description of the desired video."
    )
    
    start_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Input image to start generating video from."
    )
    
    number_of_frames: int = Field(
        161,
        json_schema_extra={"x-sr-order": 403},
        description="The number of frame count will be 8N+1 (e.g., 9, 17, 25, 161). Default: 161"
    )
    
    frames_per_second: int = Field(
        24,
        json_schema_extra={"x-sr-order": 404},
        description="Frames per second for the output video. Default: 24"
    )


class LtxvVideoFile(SunraFile):
    """Custom video file for LTX Video with predict_time."""
    pass


class LtxvVideoOutput(VideoOutput):
    """Output model for LTX Video generation with predict_time."""
    video: LtxvVideoFile
    predict_time: float = Field(
        ...,
        description="Time taken for prediction in seconds"
    )
