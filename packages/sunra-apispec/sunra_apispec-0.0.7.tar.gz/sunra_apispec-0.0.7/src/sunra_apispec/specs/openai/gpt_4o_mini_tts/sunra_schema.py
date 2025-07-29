from pydantic import BaseModel, Field
from typing import Literal
from sunra_apispec.base.output_schema import SunraFile


class TextToSpeechInput(BaseModel):
    text: str = Field(
        ...,
        title="Text",
        description="The text to generate audio for. The maximum length is 4096 characters.",
        max_length=4096,
        json_schema_extra={"x-sr-order": 201}
    )
    
    instructions: str = Field(
        default=None,
        title="Instructions",
        description="Control the voice of your generated audio with additional instructions.",
        json_schema_extra={"x-sr-order": 301}
    )
    
    voice: Literal[
        "alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer", "verse"
    ] = Field(
        default="nova",
        title="Voice",
        description="The voice to use when generating the audio. Supported voices are alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, and verse.",
        json_schema_extra={"x-sr-order": 302}
    )
    
    output_format: Literal[
        "mp3", "opus", "aac", "flac", "wav", "pcm"
    ] = Field(
        default="mp3",
        title="Output Format",
        description="The format to audio in. Supported formats are mp3, opus, aac, flac, wav, and pcm.",
        json_schema_extra={"x-sr-order": 401}
    ) 


class GPT4oMiniTTSAudioFile(SunraFile):
    duration: float

class GPT4oMiniTTSOutput(BaseModel):
    audio: GPT4oMiniTTSAudioFile
    input_token_count: int
    output_token_count: int
