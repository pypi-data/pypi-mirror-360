# Schema for Text-to-Image generation
from pydantic import BaseModel, Field
from typing import List


class TimingPrompt(BaseModel):
    """Model for a single controllable audio effect event parameter."""
    prompt: str = Field(...,
        json_schema_extra={"x-sr-order": 200},
        max_length=1500,
        description="Audio effect prompt text, max 1500 characters"
    )
    from_second: float = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Start time of the audio event, in seconds"
    )
    to_second: float = Field(
        ...,
        json_schema_extra={"x-sr-order": 302},
        description="End time of the audio event, in seconds")


class AudioGenBaseInput(BaseModel):
    """Base class for audio generation inputs"""
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 201},
        description="Random seed for generation"
    )
    
    duration: int = Field(
        default=10, 
        ge=2, 
        le=10, 
        multiple_of=1,
        json_schema_extra={"x-sr-order": 202}, 
        description="Audio duration. Default: 10 seconds. Range: 2–10 seconds."
    )


class TextToAudioInput(AudioGenBaseInput):
    """Text to audio input"""

    prompt: str = Field(
        ..., 
        json_schema_extra={"x-sr-order": 200}, 
        max_length=1500, 
        description="The prompt for the audio"
    )


class TimingToVideoInput(AudioGenBaseInput):
    """Timing to audio input"""

    timing_prompts: List[TimingPrompt] = Field(
        default_factory=list, 
        min_length=1,
        json_schema_extra={"x-sr-order": 200}, 
        description="Array of audio event parameters with timing"
    )

