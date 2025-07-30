from pydantic import BaseModel, Field
from typing import Literal


class ReplicateInput(BaseModel):
    """Input schema for HiDream I1 Fast model on Replicate"""
    
    prompt: str = Field(
        ...,
        description="Prompt"
    )
    
    model_type: Literal["fast"] = Field(
        "fast",
        description="Model type"
    )
    
    speed_mode: Literal[
        "Unsqueezed 🍋 (highest quality)",
        "Lightly Juiced 🍊 (more consistent)",
        "Juiced 🔥 (more speed)",
        "Extra Juiced 🚀 (even more speed)"
    ] = Field(
        "Lightly Juiced 🍊 (more consistent)",
        description="Speed optimization level"
    )
    
    resolution: Literal[
        "1024 × 1024 (Square)",
        "768 × 1360 (Portrait)",
        "1360 × 768 (Landscape)",
        "880 × 1168 (Portrait)",
        "1168 × 880 (Landscape)",
        "1248 × 832 (Landscape)",
        "832 × 1248 (Portrait)"
    ] = Field(
        "1024 × 1024 (Square)",
        description="Output resolution"
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


class ReplicateOutput(BaseModel):
    """Output schema for HiDream I1 Fast model on Replicate"""
    
    output: str = Field(
        ...,
        description="URL of the generated image"
    )
