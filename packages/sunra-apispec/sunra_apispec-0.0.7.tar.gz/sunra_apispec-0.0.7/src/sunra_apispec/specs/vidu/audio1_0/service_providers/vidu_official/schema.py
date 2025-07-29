"""
Schema for Vidu Official Audio API service provider.
Based on Vidu platform API documentation from:
- https://platform.vidu.com/text-to-audio
- https://platform.vidu.com/timing-to-audio
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ViduAudioModelEnum(str, Enum):
    """Available models for Vidu audio generation."""
    AUDIO1_0 = "audio1.0"


class ViduTaskStateEnum(str, Enum):
    """Task processing states."""
    CREATED = "created"
    QUEUEING = "queueing"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class ViduTimingPrompt(BaseModel):
    """Schema for timing-based sound event prompts."""
    
    from_time: float = Field(
        ...,
        alias="from",
        ge=0.0,
        description="Start timestamp for the sound event (must be >= 0 and <= duration)"
    )
    
    to: float = Field(
        ...,
        description="End timestamp for the sound event (must be >= from and <= duration)"
    )
    
    prompt: str = Field(
        ...,
        max_length=1500,
        description="Text prompt describing the sound event, maximum 1500 characters"
    )


class ViduTextToAudioInput(BaseModel):
    """Schema for text-to-audio generation using Vidu API."""
    
    model: ViduAudioModelEnum = Field(
        ...,
        description="Model name. Available value: audio1.0"
    )
    
    prompt: str = Field(
        ...,
        max_length=1500,
        description="Text prompt describing the audio. Maximum length: 1500 characters."
    )
    
    duration: Optional[float] = Field(
        10.0,
        ge=2.0,
        le=10.0,
        description="Audio duration in seconds. Default: 10 seconds. Range: 2–10 seconds."
    )
    
    seed: Optional[int] = Field(
        None,
        description="Random seed. If not provided or set to 0, a random value will be used. "
                   "Fixed value ensures reproducibility."
    )
    
    callback_url: Optional[str] = Field(
        None,
        description="Callback URL. When creating a task, you can set the callback_url "
                   "with a POST request. When the audio generation task changes its status, "
                   "Vidu will send a callback request to this URL."
    )


class ViduTimingToAudioInput(BaseModel):
    """Schema for timing-to-audio generation using Vidu API."""
    
    model: ViduAudioModelEnum = Field(
        ...,
        description="Model name. Available value: audio1.0"
    )
    
    duration: Optional[float] = Field(
        10.0,
        ge=2.0,
        le=10.0,
        description="Audio duration in seconds. Default: 10 seconds. Range: 2–10 seconds."
    )
    
    timing_prompts: List[ViduTimingPrompt] = Field(
        ...,
        min_length=1,
        description="Timeline-based sound event prompts. Each item defines a sound event "
                   "with a from and to timestamp and a prompt. "
                   "Notes: "
                   "- Max 1500 characters per event prompt. "
                   "- Events can overlap. "
                   "- from and to must be within [0, duration]."
    )
    
    seed: Optional[int] = Field(
        None,
        description="Random seed. If not provided or set to 0, a random value will be used. "
                   "Fixed value ensures reproducibility."
    )
    
    callback_url: Optional[str] = Field(
        None,
        description="Callback URL. When creating a task, you can set the callback_url "
                   "with a POST request. When the audio generation task changes its status, "
                   "Vidu will send a callback request to this URL."
    )


class ViduTextToAudioResponse(BaseModel):
    """Response schema for text-to-audio generation."""
    
    task_id: str = Field(
        ...,
        description="Vidu generated Task ID"
    )
    
    state: ViduTaskStateEnum = Field(
        ...,
        description="Task state: created, queueing, processing, success, failed"
    )
    
    model: str = Field(
        ...,
        description="Model parameter used"
    )
    
    prompt: str = Field(
        ...,
        description="Prompt text used"
    )
    
    duration: float = Field(
        ...,
        description="Audio duration in seconds"
    )
    
    seed: int = Field(
        ...,
        description="Random seed used"
    )
    
    created_at: str = Field(
        ...,
        description="Task creation timestamp (ISO8601 format)"
    )


class ViduTimingToAudioResponse(BaseModel):
    """Response schema for timing-to-audio generation."""
    
    task_id: str = Field(
        ...,
        description="Vidu generated Task ID"
    )
    
    state: ViduTaskStateEnum = Field(
        ...,
        description="Task state: created, queueing, processing, success, failed"
    )
    
    model: str = Field(
        ...,
        description="Model parameter used"
    )
    
    duration: float = Field(
        ...,
        description="Audio duration in seconds"
    )
    
    timing_prompts: List[ViduTimingPrompt] = Field(
        ...,
        description="List of configured sound events"
    )
    
    seed: int = Field(
        ...,
        description="Random seed used"
    )
    
    created_at: str = Field(
        ...,
        description="Task creation timestamp (ISO8601 format)"
    )
