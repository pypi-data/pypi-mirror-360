from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class OutputFormat(str, Enum):
    """Output format for the generated audio."""
    MP3_22050_32 = "mp3_22050_32"
    MP3_44100_32 = "mp3_44100_32"
    MP3_44100_64 = "mp3_44100_64"
    MP3_44100_96 = "mp3_44100_96"
    MP3_44100_128 = "mp3_44100_128"
    MP3_44100_192 = "mp3_44100_192"
    PCM_16000 = "pcm_16000"
    PCM_22050 = "pcm_22050"
    PCM_24000 = "pcm_24000"
    PCM_44100 = "pcm_44100"
    ULAW_8000 = "ulaw_8000"
    AAC_22050_32 = "aac_22050_32"
    AAC_44100_32 = "aac_44100_32"
    AAC_44100_64 = "aac_44100_64"
    AAC_44100_128 = "aac_44100_128"
    FLAC_22050 = "flac_22050"
    FLAC_44100 = "flac_44100"
    WAV_22050 = "wav_22050"
    WAV_44100 = "wav_44100"


class ElevenLabsSoundEffectsQueryParameters(BaseModel):
    """Query parameters for Sound Effects API."""
    output_format: OutputFormat = Field(
        default=OutputFormat.MP3_44100_128,
        description="Output format of the generated audio"
    )


class ElevenLabsSoundEffectsInput(BaseModel):
    """Input schema for ElevenLabs Sound Effects text-to-sound-effects."""
    text: str = Field(
        ...,
        description="The text that will get converted into a sound effect"
    )
    
    duration_seconds: Optional[float] = Field(
        default=None,
        ge=0.5,
        le=22.0,
        description="The duration of the sound which will be generated in seconds"
    )
    
    prompt_influence: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="A higher prompt influence makes your generation follow the prompt more closely"
    )


class ElevenLabsSoundEffectsOutput(BaseModel):
    """Output schema for ElevenLabs Sound Effects generation."""
    # The output is binary audio data
    pass
