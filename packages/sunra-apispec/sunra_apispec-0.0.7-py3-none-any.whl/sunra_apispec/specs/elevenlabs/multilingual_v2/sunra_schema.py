from pydantic import BaseModel, Field
from typing import Literal
from sunra_apispec.base.output_schema import SunraFile


class TextToSpeechInput(BaseModel):
    """Input schema for ElevenLabs Multilingual V2 text-to-speech generation."""
    
    text: str = Field(
        ...,
        max_length=10000,
        json_schema_extra={"x-sr-order": 201},
        description="The text that will get converted into speech."
    )
    
    voice: Literal[
        "Rachel (american accent, young, female)",
        "Drew (american accent, middle_aged, male)",
        "Clyde (american accent, middle_aged, male)",
        "Paul (american accent, middle_aged, male)",
        "Aria (american accent, middle_aged, female)",
        "Domi (american accent, young, female)",
        "Dave (british accent, young, male)",
        "Roger (middle_aged, male)",
        "Fin (irish accent, old, male)",
        "Sarah (american accent, young, female)",
        "Antoni (american accent, young, male)",
        "Laura (american accent, young, female)",
        "Thomas (american accent, young, male)",
        "Charlie (australian accent, young, male)",
        "George (british accent, middle_aged, male)",
        "Emily (american accent, young, female)",
        "Elli (american accent, young, female)",
        "Callum (middle_aged, male)",
        "Patrick (american accent, middle_aged, male)",
        "River (american accent, middle_aged, neutral)",
        "Harry (american accent, young, male)",
        "Liam (american accent, young, male)",
        "Dorothy (british accent, young, female)",
        "Josh (american accent, young, male)",
        "Arnold (american accent, middle_aged, male)",
        "Charlotte (swedish accent, young, female)",
        "Alice (british accent, middle_aged, female)",
        "Matilda (american accent, middle_aged, female)",
        "James (australian accent, old, male)",
        "Joseph (british accent, middle_aged, male)",
        "Will (young, male)",
        "Jeremy (irish accent, young, male)",
        "Jessica (american accent, young, female)",
        "Eric (american accent, middle_aged, male)",
        "Michael (american accent, old, male)",
        "Ethan (american accent, young, male)",
        "Chris (american accent, middle_aged, male)",
        "Gigi (american accent, young, female)",
        "Freya (american accent, young, female)",
        "Santa Claus (american accent, old, male)",
        "Brian (american accent, middle_aged, male)",
        "Grace (us-southern accent, young, female)",
        "Daniel (british accent, middle_aged, male)",
        "Lily (british accent, middle_aged, female)",
        "Serena (american accent, middle_aged, female)",
        "Adam ( accent, middle_aged, male)",
        "Nicole (american accent, young, female)",
        "Bill (american accent, old, male)",
        "Jessie (american accent, old, male)",
        "Sam (american accent, young, male)",
        "Glinda (american accent, middle_aged, female)",
        "Giovanni (italian accent, young, male)",
        "Mimi (swedish accent, young, female)"
    ] = Field(
        default="Rachel (american accent, young, female)",
        json_schema_extra={"x-sr-order": 301},
        description="Voice from provided_voices"
    )
    
    output_format: Literal[
        "mp3_22050_32",
        "mp3_44100_32",
        "mp3_44100_64",
        "mp3_44100_96",
        "mp3_44100_128",
        "mp3_44100_192",
        "pcm_8000",
        "pcm_16000",
        "pcm_22050",
        "pcm_24000",
        "pcm_44100",
        "pcm_48000",
        "ulaw_8000",
        "alaw_8000",
        "opus_48000_32",
        "opus_48000_64",
        "opus_48000_96",
        "opus_48000_128",
        "opus_48000_192"
    ] = Field(
        default="mp3_44100_128",
        json_schema_extra={"x-sr-order": 400},
        description="Output format from output_format_list"
    )
    
    stability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 401},
        description="Voice stability (0-1). Default: 0.5"
    )
    
    similarity_boost: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 402},
        description="Similarity boost (0-1). Default: 0.75"
    )
    
    style: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 403},
        description="Style exaggeration (0-1)."
    )
    
    speaker_boost: bool = Field(
        default=True,
        json_schema_extra={"x-sr-order": 404},
        description="Boosts speaker similarity."
    )
    
    speed: float = Field(
        default=1.0,
        ge=0.7,
        le=1.2,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 405},
        description="Audio speed (0.7-1.2). Default: 1.0"
    )

class MultilingualV2Output(BaseModel):
    """Output schema for ElevenLabs Multilingual V2 text-to-speech generation."""
    audio: SunraFile
    input_character_count: int
