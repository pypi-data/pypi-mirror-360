from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from pydantic import HttpUrl


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


class SpeechToTextInput(BaseModel):
    """Input schema for ElevenLabs Scribe V1 speech-to-text transcription."""
    
    audio: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Audio file URL."
    )
    
    language: Literal[
        "Arabic",
        "Chinese", 
        "English",
        "French",
        "German",
        "Hindi",
        "Italian",
        "Japanese",
        "Korean",
        "Portuguese",
        "Russian",
        "Spanish",
        "Turkish",
        "Bengali",
        "Dutch",
        "Indonesian",
        "Persian",
        "Swahili",
        "Thai",
        "Vietnamese"
    ] = Field(
        default="English",
        json_schema_extra={"x-sr-order": 401},
        description="Supported languages from provided_languages."
    )
    
    tag_audio_events: bool = Field(
        default=True,
        json_schema_extra={"x-sr-order": 402},
        description="Tag audio events."
    )
    
    speaker_diarization: bool = Field(
        default=False,
        json_schema_extra={"x-sr-order": 403},
        description="Enable speaker diarization."
    )


class ScribeV1Output(BaseModel):
    """Output schema for ElevenLabs Scribe V1 transcription results."""
    language_code: str = Field(..., description="The detected language code")
    language_probability: float = Field(..., description="The confidence score of the language detection (0 to 1)")
    text: str = Field(..., description="The raw text of the transcription")
    words: List[WordInfo] = Field(..., description="List of words with their timing information")
    input_audio_duration: int = Field(..., description="The duration of the input audio in seconds")
