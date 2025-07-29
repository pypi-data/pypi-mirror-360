from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class AudioFile(BaseModel):
    """Audio file output schema."""
    url: str = Field(description="The URL where the file can be downloaded from.")
    content_type: Optional[str] = Field(default=None, description="The mime type of the file.")
    file_name: Optional[str] = Field(default=None, description="The name of the file.")
    file_size: Optional[int] = Field(default=None, description="The size of the file in bytes.")
    duration: float = Field(description="The duration of the audio file in seconds.")


class LDMVoiceInput(BaseModel):
    """Voice configuration for dialogue speakers."""
    voice: str = Field(
        ..., 
        description="The unique ID of a PlayHT or Cloned Voice, or a name from the available presets."
    )
    turn_prefix: str = Field(
        default="Speaker 1: ",
        description="A prefix to identify the speaker in multi-turn dialogues."
    )


class FalPlayaiTtsDialogInput(BaseModel):
    """FAL input schema for PlayAI dialog TTS."""
    
    input: str = Field(
        ...,
        min_length=1,
        description="The dialogue text with turn prefixes to distinguish speakers."
    )
    
    voices: List[LDMVoiceInput] = Field(
        default=[
            LDMVoiceInput(voice="Jennifer (English (US)/American)", turn_prefix="Speaker 1: "),
            LDMVoiceInput(voice="Furio (English (IT)/Italian)", turn_prefix="Speaker 2: ")
        ],
        description="A list of voice definitions for each speaker in the dialogue. Must be between 1 and 2 voices."
    )
    
    response_format: Literal["url", "bytes"] = Field(
        default="url",
        description="The format of the response. Default value: 'url'"
    )
    
    seed: Optional[int] = Field(
        default=None,
        ge=0,
        description="An integer number greater than or equal to 0. If equal to null or not provided, a random seed will be used. Useful to control the reproducibility of the generated audio. Assuming all other properties didn't change, a fixed seed should always generate the exact same audio file."
    )


class FalPlayaiTtsDialogOutput(BaseModel):
    """FAL output schema for PlayAI dialog TTS."""
    audio: AudioFile = Field(description="The generated audio file.")
