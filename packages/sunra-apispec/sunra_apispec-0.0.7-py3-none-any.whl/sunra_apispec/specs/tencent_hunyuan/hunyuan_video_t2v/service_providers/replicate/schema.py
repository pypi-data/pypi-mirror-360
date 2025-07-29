from typing import Optional
from pydantic import BaseModel, Field


class ReplicateInput(BaseModel):
    """Replicate input schema for Tencent Hunyuan Video T2V model."""
    prompt: str = Field(
        default="A cat walks on the grass, realistic style",
        description="The prompt to guide the video generation"
    )
    width: int = Field(
        default=864, 
        ge=16, 
        le=1280,
        description="Width of the video in pixels (must be divisible by 16)"
    )
    height: int = Field(
        default=480, 
        ge=16, 
        le=1280,
        description="Height of the video in pixels (must be divisible by 16)"
    )
    video_length: int = Field(
        default=129, 
        ge=1, 
        le=200,
        description="Number of frames to generate (must be 4k+1, ex: 49 or 129)"
    )
    infer_steps: int = Field(
        default=50, 
        ge=1,
        description="Number of denoising steps"
    )
    embedded_guidance_scale: float = Field(
        default=6.0, 
        ge=1.0, 
        le=10.0,
        description="Guidance scale"
    )
    fps: int = Field(
        default=24, 
        ge=1,
        description="Frames per second of the output video"
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed (leave empty for random)"
    )
