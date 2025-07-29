from typing import Literal, Optional
from pydantic import BaseModel, Field


class ReplicateInput(BaseModel):
    """Input model for Replicate Wan 2.1 1.3B API."""
    
    prompt: str = Field(
        ...,
        description="Text prompt describing what you want to generate"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducible results (leave blank for random)"
    )
    
    frame_num: int = Field(
        default=81,
        description="Video duration in frames (based on standard 16fps playback)"
    )
    
    resolution: Literal["480p"] = Field(
        default="480p",
        description="Video resolution"
    )
    
    aspect_ratio: Literal["16:9"] = Field(
        default="16:9",
        description="Video aspect ratio"
    )
    
    sample_shift: float = Field(
        default=8,
        ge=1,
        le=20,
        description="Sampling shift factor for flow matching (recommended range: 8-12)"
    )
    
    sample_steps: int = Field(
        default=30,
        ge=10,
        le=50,
        description="Number of sampling steps (higher = better quality but slower)"
    )
    
    sample_guide_scale: float = Field(
        default=6,
        ge=1,
        le=20,
        description="Classifier free guidance scale (higher values strengthen prompt adherence)"
    ) 