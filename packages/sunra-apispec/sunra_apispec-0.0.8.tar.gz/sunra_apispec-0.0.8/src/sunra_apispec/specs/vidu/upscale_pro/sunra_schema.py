# Schema for Upscale Pro video generation
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Literal

class UpscaleProInput(BaseModel):
    """Upscale Pro input"""
    video: HttpUrl | str = Field(
        ..., 
        json_schema_extra={"x-sr-order": 200}, 
        description="The URL of the video to be upscaled. Maximum video duration: 300 seconds."
    )

    resolution: Literal['1080p', '2K', '4K', '8K'] = Field(
        '1080p', 
        json_schema_extra={"x-sr-order": 401}, 
        description="Target resolution for upscaling. The resolution must be higher than the original video resolution, otherwise the task will fail."
    )
