from pydantic import BaseModel, Field
from typing import Literal, Optional


class OpenAITTSInput(BaseModel):
    input: str = Field(
        ...,
        max_length=4096,
        description="The text to generate audio for. The maximum length is 4096 characters."
    )
    
    model: Literal["tts-1", "tts-1-hd", "gpt-4o-mini-tts"] = Field(
        default="gpt-4o-mini-tts",
        description="One of the available TTS models: tts-1, tts-1-hd or gpt-4o-mini-tts."
    )
    
    voice: Literal[
        "alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer", "verse"
    ] = Field(
        ...,
        description="The voice to use when generating the audio."
    )
    
    instructions: Optional[str] = Field(
        default=None,
        description="Control the voice of your generated audio with additional instructions. Does not work with tts-1 or tts-1-hd."
    )
    
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = Field(
        default="mp3",
        description="The format to audio in. Supported formats are mp3, opus, aac, flac, wav, and pcm."
    )
    
    speed: Optional[float] = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="The speed of the generated audio. Select a value from 0.25 to 4.0. 1.0 is the default. Does not work with gpt-4o-mini-tts."
    )


class OpenAITTSOutput(BaseModel):
    # OpenAI returns binary audio data directly
    pass
