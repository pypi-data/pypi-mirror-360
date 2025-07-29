from pydantic import BaseModel, Field
from typing import Literal
from sunra_apispec.base.output_schema import AudioOutput


class TextToSoundEffectsInput(BaseModel):
    """Input schema for ElevenLabs Sound Effects text-to-sound-effects generation."""
    
    text: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="The text that will get converted into a sound effect."
    )
    
    output_format: Literal[
        "mp3_22050_32",
        "mp3_44100_32",
        "mp3_44100_64",
        "mp3_44100_96",
        "mp3_44100_128",
        "mp3_44100_192",
        "pcm_8000",
        "pcm_16000",
        "pcm_22050",
        "pcm_24000",
        "pcm_44100",
        "pcm_48000",
        "ulaw_8000",
        "alaw_8000",
        "opus_48000_32",
        "opus_48000_64",
        "opus_48000_96",
        "opus_48000_128",
        "opus_48000_192"
    ] = Field(
        default="mp3_44100_128",
        json_schema_extra={"x-sr-order": 400},
        description="Output format from output_format_list"
    )
    
    duration: float = Field(
        default=None,
        ge=0.5,
        le=22.0,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 401},
        description="Duration in seconds (0.5-22). Default: None (auto-detect)."
    )
    
    prompt_influence: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 402},
        description="Influence of prompt (0-1). Default: 0.3."
    )


class SoundEffectsOutput(AudioOutput): 
    pass