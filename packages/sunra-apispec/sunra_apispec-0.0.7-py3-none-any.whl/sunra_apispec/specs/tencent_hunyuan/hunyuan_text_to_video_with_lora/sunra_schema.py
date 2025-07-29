from pydantic import BaseModel, Field, HttpUrl
from typing import Literal
from sunra_apispec.base.output_schema import VideoOutput, SunraFile


class TextToVideoInput(BaseModel):
    """Input model for text-to-video generation using Hunyuan Video with LoRA."""
    
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        min_length=1,
        max_length=32000,
        description="The text prompt describing your video scene."
    )
    
    lora_url: str = Field(
        ...,
        title="LoRA Url",
        json_schema_extra={"x-sr-order": 301},
        description="A URL pointing to your LoRA .safetensors file or a Hugging Face repo (e.g. 'user/repo' - uses the first .safetensors file)."
    )
    
    lora_strength: float = Field(
        1.0,
        ge=-10.0,
        le=10.0,
        multiple_of=0.01,
        title="LoRA Strength",
        json_schema_extra={"x-sr-order": 302},
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
        json_schema_extra={"x-sr-order": 303},
        description="Algorithm used to generate the video frames."
    )
    
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 304},
        description="Set a seed for reproducibility. Random by default."
    )
    
    guidance_scale: float = Field(
        6.0,
        ge=0.0,
        le=30.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 305},
        description="Overall influence of text vs. model."
    )
    
    number_of_steps: int = Field(
        30,
        ge=1,
        le=150,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 306},
        description="Number of diffusion steps."
    )
    
    width: int = Field(
        640,
        ge=64,
        le=1536,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 401},
        description="Width for the generated video."
    )
    
    height: int = Field(
        360,
        ge=64,
        le=1024,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 402},
        description="Height for the generated video."
    )
    
    number_of_frames: int = Field(
        33,
        ge=1,
        le=1440,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 403},
        description="How many frames (duration) in the resulting video."
    )
    
    frames_per_second: int = Field(
        16,
        ge=1,
        le=60,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 404},
        description="Video frame rate."
    )
    
    enhance_weight: float = Field(
        0.3,
        ge=0.0,
        le=2.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 405},
        description="Strength of the video enhancement effect."
    )
    
    enhance_single: bool = Field(
        True,
        json_schema_extra={"x-sr-order": 406},
        description="Apply enhancement to individual frames."
    )
    
    enhance_double: bool = Field(
        True,
        json_schema_extra={"x-sr-order": 407},
        description="Apply enhancement across frame pairs."
    )
    
    enhance_start: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 408},
        description="When to start enhancement in the video. Must be less than enhance_end."
    )
    
    enhance_end: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 409},
        description="When to end enhancement in the video. Must be greater than enhance_start."
    )
    
    flow_shift: int = Field(
        9,
        ge=0,
        le=20,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 410},
        description="Video continuity factor (flow)."
    )
    
    denoise_strength: float = Field(
        1.0,
        ge=0.0,
        le=2.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 411},
        description="Controls how strongly noise is applied each step."
    )
    
    force_offload: bool = Field(
        True,
        json_schema_extra={"x-sr-order": 412},
        description="Whether to force model layers offloaded to CPU."
    )
    
    crf: int = Field(
        19,
        ge=0,
        le=51,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 413},
        description="CRF (quality) for H264 encoding. Lower values = higher quality."
    )


class HunyuanVideoLoraFile(SunraFile):
    """Custom video file for Hunyuan Video LoRA."""
    pass


class HunyuanVideoLoraOutput(VideoOutput):
    """Output model for Hunyuan Video LoRA generation with predict_time."""
    video: HunyuanVideoLoraFile
    predict_time: float = Field(
        ...,
        description="Time taken for prediction in seconds"
    )
