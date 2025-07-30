from pydantic import BaseModel, Field
from pydantic import HttpUrl
from sunra_apispec.base.output_schema import AudioOutput


class AudioIsolationInput(BaseModel):
    """Input schema for ElevenLabs Voice Isolater audio isolation."""
    
    audio: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Audio file URL."
    ) 


class VoiceIsolaterOutput(AudioOutput):
    input_audio_duration: int