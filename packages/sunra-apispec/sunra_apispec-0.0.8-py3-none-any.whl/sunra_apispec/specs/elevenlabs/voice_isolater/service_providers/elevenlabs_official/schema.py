from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class FileFormat(str, Enum):
    """Input file format options."""
    PCM_S16LE_16 = "pcm_s16le_16"
    OTHER = "other"


class ElevenLabsVoiceIsolaterInput(BaseModel):
    """Input schema for ElevenLabs Voice Isolater audio isolation."""
    audio: Optional[bytes] = Field(
        default=None,
        description="The audio file from which vocals/speech will be isolated from (binary data)"
    )
    
    file_format: Optional[FileFormat] = Field(
        default=FileFormat.OTHER,
        description="The format of input audio"
    )


class ElevenLabsVoiceIsolaterOutput(BaseModel):
    """Output schema for ElevenLabs Voice Isolater audio isolation."""
    # The output is binary audio data
    pass
