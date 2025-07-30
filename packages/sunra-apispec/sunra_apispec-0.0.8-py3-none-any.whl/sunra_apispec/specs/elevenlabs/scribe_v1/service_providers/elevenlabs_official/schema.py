from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class TimestampsGranularity(str, Enum):
    """Granularity options for timestamps."""
    NONE = "none"
    WORD = "word"
    CHARACTER = "character"


class FileFormat(str, Enum):
    """Input file format options."""
    PCM_S16LE_16 = "pcm_s16le_16"
    OTHER = "other"


class AdditionalFormat(BaseModel):
    """Additional format for transcript export."""
    requested_format: Optional[str] = Field(None, description="The requested format for the transcript")
    file_extension: Optional[str] = Field(None, description="File extension for the format")
    content_type: Optional[str] = Field(None, description="MIME type of the format")
    is_base64_encoded: Optional[bool] = Field(None, description="Whether the content is base64 encoded")
    content: Optional[str] = Field(None, description="The actual content in the requested format")


class ElevenLabsScribeV1QueryParameters(BaseModel):
    """Query parameters for Scribe V1 API."""
    enable_logging: bool = Field(
        default=True,
        description="When enable_logging is set to false zero retention mode will be used for the request"
    )


class ElevenLabsScribeV1Input(BaseModel):
    """Input schema for ElevenLabs Scribe V1 speech-to-text."""
    model_id: str = Field(
        default="scribe_v1",
        description="The ID of the model to use for transcription"
    )
    
    file: Optional[bytes] = Field(
        default=None,
        description="The file to transcribe (binary data)"
    )
    
    language_code: Optional[str] = Field(
        default=None,
        description="An ISO-639-1 or ISO-639-3 language_code corresponding to the language of the audio file"
    )
    
    tag_audio_events: bool = Field(
        default=True,
        description="Whether to tag audio events like (laughter), (footsteps), etc. in the transcription"
    )
    
    num_speakers: Optional[int] = Field(
        default=None,
        ge=1,
        le=32,
        description="The maximum amount of speakers talking in the uploaded file"
    )
    
    timestamps_granularity: TimestampsGranularity = Field(
        default=TimestampsGranularity.WORD,
        description="The granularity of the timestamps in the transcription"
    )
    
    diarize: bool = Field(
        default=False,
        description="Whether to annotate which speaker is currently talking in the uploaded file"
    )
    
    additional_formats: Optional[List[AdditionalFormat]] = Field(
        default=None,
        description="A list of additional formats to export the transcript to"
    )
    
    file_format: FileFormat = Field(
        default=FileFormat.OTHER,
        description="The format of input audio"
    )
    
    cloud_storage_url: Optional[str] = Field(
        default=None,
        description="The valid AWS S3, Cloudflare R2 or Google Cloud Storage URL of the file to transcribe"
    )


class CharacterInfo(BaseModel):
    """Character-level timing information."""
    text: str = Field(..., description="The character")
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")


class WordInfo(BaseModel):
    """Word-level timing and speaker information."""
    text: str = Field(..., description="The word text")
    type: Literal["word", "spacing"] = Field(..., description="Type of the element")
    logprob: float = Field(..., description="Log probability of the word")
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    speaker_id: Optional[str] = Field(None, description="Speaker identifier (when diarization is enabled)")
    characters: Optional[List[CharacterInfo]] = Field(None, description="Character-level timing information")


class ElevenLabsScribeV1Output(BaseModel):
    """Output schema for ElevenLabs Scribe V1 transcription results."""
    language_code: str = Field(..., description="The detected language code")
    language_probability: float = Field(..., description="The confidence score of the language detection (0 to 1)")
    text: str = Field(..., description="The raw text of the transcription")
    words: List[WordInfo] = Field(..., description="List of words with their timing information")
    additional_formats: Optional[List[AdditionalFormat]] = Field(None, description="Requested additional formats of the transcript")
