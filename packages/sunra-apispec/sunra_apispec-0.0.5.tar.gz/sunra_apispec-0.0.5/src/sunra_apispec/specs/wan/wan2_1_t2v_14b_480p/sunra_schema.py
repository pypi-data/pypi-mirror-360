# Schema for Text-to-Video generation
from pydantic import BaseModel, Field
from typing import Literal
from sunra_apispec.base.output_schema import VideoOutput, SunraFile

class TextToVideoInput(BaseModel):
    """Input model for text-to-video generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt for video generation.",
    )
    
    number_of_steps: int = Field(
        default=30,
        ge=1,
        le=40,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 204},
        description="Number of sampling steps (higher = better quality but slower).",
    )
    
    guidance_scale: float = Field(
        default=5.0,
        ge=0,
        le=10.0,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 205},
        description="Classifier free guidance scale (higher values strengthen prompt adherence).",
    )
    
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 206},
        description="Random seed for reproducibility.",
    )
    
    aspect_ratio: Literal["16:9", "9:16"] = Field(
        "16:9",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of video. 16:9 corresponds to landscape, and 9:16 is portrait.",
    )
    
    number_of_frames: int = Field(
        default=81,
        ge=81,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 404},
        description="Number of video frames. Standard value is 81 frames.",
    )
    
    frames_per_second: int = Field(
        default=16,
        ge=5,
        le=24,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 405},
        description="Frames per second for video playback.",
    )
    
    fast_mode: Literal["Off", "On"] = Field(
        "Off",
        json_schema_extra={"x-sr-order": 501},
        description="Speed up generation with different levels of acceleration. Faster modes may degrade quality somewhat.",
    )


class Wan21T2V14B480PVideoFile(SunraFile):
    duration: int = Field(
        ...,
        description="Duration of the video in seconds",
    )

class Wan21T2V14B480POutput(VideoOutput):
    video: Wan21T2V14B480PVideoFile
