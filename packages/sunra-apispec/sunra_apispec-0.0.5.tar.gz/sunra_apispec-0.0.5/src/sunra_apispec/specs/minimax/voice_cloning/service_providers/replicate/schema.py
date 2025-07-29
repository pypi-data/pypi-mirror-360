# Schema for MiniMax voice Generation
from pydantic import BaseModel, Field
from enum import Enum

class SpeechModel(str, Enum):
    SPEECH_02_TURBO = "speech-02-turbo"
    SPEECH_02_HD = "speech-02-hd"

class MinimaxVoiceInput(BaseModel):
    """
    Input Schema for Replicate's Minimax Voice Cloning
    """
    voice_file: str = Field(
        ...,
        description="Voice file to clone. Must be MP3, M4A, or WAV format, 10s to 5min duration, and less than 20MB.",
        json_schema_extra={"x-order": 0}
    )
    need_noise_reduction: bool = Field(
        default=False,
        description="Enable noise reduction. Use this if the voice file has background noise.",
        json_schema_extra={"x-order": 1}
    )
    model: SpeechModel = Field(
        default=SpeechModel.SPEECH_02_TURBO,
        description="The text-to-speech model to train",
        json_schema_extra={"x-order": 2}
    )
    accuracy: float = Field(
        default=0.7,
        ge=0,
        le=1,
        description="Text validation accuracy threshold (0-1)",
        json_schema_extra={"x-order": 3}
    )
    need_volume_normalization: bool = Field(
        default=False,
        description="Enable volume normalization",
        json_schema_extra={"x-order": 4}
    )

class MinimaxVoiceOutput(BaseModel):
    """
    Output Schema for Replicate's Minimax Voice Cloning
    """
    voice_id: str = Field(
        ...,
        description="The ID of the voice that was cloned",
    )

    model: SpeechModel = Field(
        ...,
        description="The text-to-speech model to train",
    )

    preview: str = Field(
        ...,
        description="The preview of the voice that was cloned",
    )
