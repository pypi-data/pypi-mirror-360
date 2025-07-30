from typing import Literal, Optional
from pydantic import BaseModel, Field


class ReplicateInput(BaseModel):
    """Input model for Replicate Wan 1.3B Inpaint API."""
    
    input_video: str = Field(
        ...,
        description="Original video to be inpainted"
    )
    
    prompt: str = Field(
        ...,
        description="Prompt for inpainting the masked area"
    )
    
    mask_video: Optional[str] = Field(
        default=None,
        description="Mask video (white areas will be inpainted). Leave blank for video-to-video"
    )
    
    negative_prompt: Optional[str] = Field(
        default=None,
        description="Negative prompt"
    )
    
    seed: int = Field(
        default=-1,
        description="Random seed. Leave blank for random"
    )
    
    strength: float = Field(
        default=0.9,
        le=1.0,
        description="Strength of inpainting effect, 1.0 is full regeneration"
    )
    
    expand_mask: int = Field(
        default=10,
        le=100,
        description="Expand the mask by a number of pixels"
    )
    
    guide_scale: float = Field(
        default=5,
        ge=1,
        le=15,
        description="Guidance scale for prompt adherence"
    )
    
    sampling_steps: int = Field(
        default=50,
        ge=20,
        le=100,
        description="Number of sampling steps"
    )
    
    frames_per_second: int = Field(
        default=16,
        ge=5,
        le=30,
        description="Output video FPS"
    )
    
    keep_aspect_ratio: bool = Field(
        default=False,
        description="Keep the aspect ratio of the input video. This will degrade the quality of the inpainting."
    )
    
    inpaint_fixup_steps: Optional[int] = Field(
        default=None,
        le=10,
        description="Number of steps for final inpaint fixup. Ignored when in video-to-video mode (when mask_video is empty)"
    ) 