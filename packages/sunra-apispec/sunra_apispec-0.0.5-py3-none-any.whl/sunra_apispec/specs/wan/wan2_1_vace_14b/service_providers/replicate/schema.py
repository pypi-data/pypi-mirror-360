from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ReplicateInput(BaseModel):
    """Input model for Replicate VACE 1.3B API."""
    
    prompt: str = Field(
        ...,
        description="Prompt"
    )
    
    seed: int = Field(
        default=-1,
        description="Random seed (-1 for random)"
    )
    
    size: Literal[
        "480*832",
        "832*480",
        "1280*720",
        "720*1280"
    ] = Field(
        default="1280*720",
        description="Output resolution"
    )
    
    frame_num: int = Field(
        default=81,
        description="Number of frames to generate."
    )
    
    speed_mode: str = Field(
        default="Lightly Juiced 🍋 (more consistent)",
        description="Speed optimization level"
    )
    
    sample_shift: int = Field(
        default=16,
        description="Sample shift"
    )
    
    sample_steps: int = Field(
        default=50,
        description="Sample steps"
    )
    
    sample_solver: Literal["unipc"] = Field(
        default="unipc",
        description="Sample solver"
    )
    
    sample_guide_scale: float = Field(
        default=5,
        description="Sample guide scale"
    )
    
    src_video: Optional[str] = Field(
        default=None,
        description="Input video to edit."
    )
    
    src_mask: Optional[str] = Field(
        default=None,
        description="Input mask video to edit."
    )
    
    src_ref_images: Optional[List[str]] = Field(
        default=None,
        description="Input reference images to edit."
    ) 