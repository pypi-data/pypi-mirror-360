from pydantic import BaseModel, Field
from typing import Literal


class ReplicateInput(BaseModel):
    """Input schema for Replicate Hunyuan Video LoRA API based on openapi.json."""
    
    prompt: str = Field(
        "",
        description="The text prompt describing your video scene."
    )
    
    lora_url: str = Field(
        "",
        description="A URL pointing to your LoRA .safetensors file or a Hugging Face repo (e.g. 'user/repo' - uses the first .safetensors file)."
    )
    
    lora_strength: float = Field(
        1.0,
        ge=-10.0,
        le=10.0,
        multiple_of=0.01,
        description="Scale/strength for your LoRA."
    )
    
    scheduler: Literal[
        "FlowMatchDiscreteScheduler",
        "SDE-DPMSolverMultistepScheduler",
        "DPMSolverMultistepScheduler", 
        "SASolverScheduler",
        "UniPCMultistepScheduler"
    ] = Field(
        "DPMSolverMultistepScheduler",
        description="Algorithm used to generate the video frames."
    )
    
    steps: int = Field(
        50,
        ge=1,
        le=150,
        multiple_of=1,
        description="Number of diffusion steps."
    )
    
    guidance_scale: float = Field(
        6.0,
        ge=0.0,
        le=30.0,
        multiple_of=0.01,
        description="Overall influence of text vs. model."
    )
    
    flow_shift: int = Field(
        9,
        ge=0,
        le=20,
        multiple_of=1,
        description="Video continuity factor (flow)."
    )
    
    num_frames: int = Field(
        33,
        ge=1,
        le=1440,
        multiple_of=1,
        description="How many frames (duration) in the resulting video."
    )
    
    width: int = Field(
        640,
        ge=64,
        le=1536,
        multiple_of=1,
        description="Width for the generated video."
    )
    
    height: int = Field(
        360,
        ge=64,
        le=1024,
        multiple_of=1,
        description="Height for the generated video."
    )
    
    denoise_strength: float = Field(
        1.0,
        ge=0.0,
        le=2.0,
        multiple_of=0.01,
        description="Controls how strongly noise is applied each step."
    )
    
    force_offload: bool = Field(
        True,
        description="Whether to force model layers offloaded to CPU."
    )
    
    frame_rate: int = Field(
        16,
        ge=1,
        le=60,
        multiple_of=1,
        description="Video frame rate."
    )
    
    crf: int = Field(
        19,
        ge=0,
        le=51,
        multiple_of=1,
        description="CRF (quality) for H264 encoding. Lower values = higher quality."
    )
    
    enhance_weight: float = Field(
        0.3,
        ge=0.0,
        le=2.0,
        multiple_of=0.01,
        description="Strength of the video enhancement effect."
    )
    
    enhance_single: bool = Field(
        True,
        description="Apply enhancement to individual frames."
    )
    
    enhance_double: bool = Field(
        True,
        description="Apply enhancement across frame pairs."
    )
    
    enhance_start: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        description="When to start enhancement in the video. Must be less than enhance_end."
    )
    
    enhance_end: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        description="When to end enhancement in the video. Must be greater than enhance_start."
    )
    
    seed: int | None = Field(
        None,
        description="Set a seed for reproducibility. Random by default."
    )
    
    replicate_weights: str | None = Field(
        None,
        description="A .tar file containing LoRA weights from replicate."
    )
