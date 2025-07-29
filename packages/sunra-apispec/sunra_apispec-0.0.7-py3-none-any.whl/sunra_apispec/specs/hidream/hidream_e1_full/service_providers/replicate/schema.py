from pydantic import BaseModel, Field
from typing import Literal


class ReplicateInput(BaseModel):
    """Input schema for HiDream E1 Full model on Replicate"""
    
    prompt: str = Field(
        ...,
        description="Prompt"
    )
    
    speed_mode: Literal[
        "Lightly Juiced 🍊 (more consistent)",
        "Juiced 🔥 (more speed)",
        "Extra Juiced 🚀 (even more speed)"
    ] = Field(
        "Lightly Juiced 🍊 (more consistent)",
        description="Speed optimization level"
    )
    
    image: str = Field(
        ...,
        description="Input image to edit"
    )
    
    seed: int = Field(
        -1,
        description="Random seed (-1 for random)"
    )
    
    output_format: Literal["png", "jpg", "webp"] = Field(
        "webp",
        description="Output format"
    )
    
    output_quality: int = Field(
        100,
        ge=1,
        le=100,
        description="Output quality (for jpg and webp)"
    )
    
    guidance_scale: float = Field(
        5.0,
        ge=0.0,
        le=10.0,
        description="Guidance scale"
    )
    
    num_inference_steps: int = Field(
        28,
        ge=1,
        le=1000,
        description="Number of inference steps"
    )
    
    image_guidance_scale: float = Field(
        4.0,
        ge=0.0,
        le=10.0,
        description="Image guidance scale"
    )


class ReplicateOutput(BaseModel):
    """Output schema for HiDream E1 Full model on Replicate"""
    
    output: str = Field(
        ...,
        description="URL of the generated image"
    )
