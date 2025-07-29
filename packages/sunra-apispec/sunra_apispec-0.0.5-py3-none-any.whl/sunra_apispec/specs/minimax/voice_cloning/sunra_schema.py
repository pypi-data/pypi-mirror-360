from pydantic import BaseModel, Field, HttpUrl
from typing import Literal

class VoiceCloningInput(BaseModel):
    """
    Input schema for voice cloning.
    """
    voice_reference: HttpUrl | str = Field(
        ...,
        description="Voice file to clone. Must be MP3, M4A, or WAV format, 10s to 5min duration, and less than 20MB.",
        json_schema_extra={"x-sr-order": 301}
    )
    noise_reduction: bool = Field(
        default=False,
        description="Enable noise reduction. Use this if the voice file has background noise.",
        json_schema_extra={"x-sr-order": 302}
    )
    model: Literal["speech-02-turbo", "speech-02-hd"] = Field(
        default="speech-02-turbo",
        description="The text-to-speech model to train",
        json_schema_extra={"x-sr-order": 303}
    )
    accuracy: float = Field(
        default=0.7,
        ge=0,
        le=1,
        multiple_of=0.01,
        description="Text validation accuracy threshold (0-1)",
        json_schema_extra={"x-sr-order": 304}
    )
    volume_normalization: bool = Field(
        default=False,
        description="Enable volume normalization",
        json_schema_extra={"x-sr-order": 401}
    )


class VoiceCloningOutput(BaseModel):
    """
    Output schema for voice cloning.
    """ 
    voice_id: str = Field(
        ...,
        description="The ID of the voice that was cloned",
        json_schema_extra={"x-sr-order": 402}
    )
