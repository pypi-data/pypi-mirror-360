from pydantic import BaseModel, Field
from typing import Optional, Literal


class AudioFile(BaseModel):
    """Audio file output schema."""
    url: str = Field(description="The URL where the file can be downloaded from.")
    content_type: Optional[str] = Field(default=None, description="The mime type of the file.")
    file_name: Optional[str] = Field(default=None, description="The name of the file.")
    file_size: Optional[int] = Field(default=None, description="The size of the file in bytes.")
    duration: float = Field(description="The duration of the audio file in seconds.")


class FalPlayaiPlay30MiniInput(BaseModel):
    """FAL input schema for PlayAI TTS V3."""
    
    input: str = Field(
        ...,
        min_length=1,
        description="The text to be converted to speech."
    )
    
    voice: str = Field(
        ...,
        description="The unique ID of a PlayHT or Cloned Voice, or a name from the available presets."
    )
    
    response_format: Literal["url", "bytes"] = Field(
        default="url",
        description="The format of the response."
    )
    
    seed: Optional[int] = Field(
        default=None,
        ge=0,
        description="An integer number greater than or equal to 0. If equal to null or not provided, a random seed will be used. Useful to control the reproducibility of the generated audio. Assuming all other properties didn't change, a fixed seed should always generate the exact same audio file."
    )


class FalPlayaiPlay30MiniOutput(BaseModel):
    """FAL output schema for PlayAI Play 3.0 Mini."""
    audio: AudioFile = Field(description="The generated audio file.") 