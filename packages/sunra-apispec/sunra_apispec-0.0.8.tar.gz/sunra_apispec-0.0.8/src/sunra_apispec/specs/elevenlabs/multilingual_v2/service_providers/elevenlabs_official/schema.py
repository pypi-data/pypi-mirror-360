from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class OutputFormat(str, Enum):
    """Output format for the generated audio."""
    MP3_22050_32 = "mp3_22050_32"
    MP3_44100_32 = "mp3_44100_32"
    MP3_44100_64 = "mp3_44100_64"
    MP3_44100_96 = "mp3_44100_96"
    MP3_44100_128 = "mp3_44100_128"
    MP3_44100_192 = "mp3_44100_192"
    PCM_8000 = "pcm_8000"
    PCM_16000 = "pcm_16000"
    PCM_22050 = "pcm_22050"
    PCM_24000 = "pcm_24000"
    PCM_44100 = "pcm_44100"
    PCM_48000 = "pcm_48000"
    ULAW_8000 = "ulaw_8000"
    ALAW_8000 = "alaw_8000"
    OPUS_48000_32 = "opus_48000_32"
    OPUS_48000_64 = "opus_48000_64"
    OPUS_48000_96 = "opus_48000_96"
    OPUS_48000_128 = "opus_48000_128"
    OPUS_48000_192 = "opus_48000_192"


class ApplyTextNormalization(str, Enum):
    """Text normalization options."""
    AUTO = "auto"
    ON = "on"
    OFF = "off"


class VoiceSettings(BaseModel):
    """Voice settings for the text-to-speech conversion."""
    stability: Optional[float] = Field(
        default=None,
        description="Determines how stable the voice is and the randomness between each generation. Lower values introduce broader emotional range for the voice. Higher values can result in a monotonous voice with limited emotion."
    )
    similarity_boost: Optional[float] = Field(
        default=None,
        description="Determines how closely the AI should adhere to the original voice when attempting to replicate it."
    )
    style: Optional[float] = Field(
        default=None,
        description="Determines the style exaggeration of the voice. This setting attempts to amplify the style of the original speaker. It does consume additional computational resources and might increase latency if set to anything other than 0."
    )
    use_speaker_boost: Optional[bool] = Field(
        default=None,
        description="This setting boosts the similarity to the original speaker. Using this setting requires a slightly higher computational load, which in turn increases latency."
    )
    speed: Optional[float] = Field(
        default=None,
        description="Adjusts the speed of the voice. A value of 1.0 is the default speed, while values less than 1.0 slow down the speech, and values greater than 1.0 speed it up."
    )


class PronunciationDictionaryLocator(BaseModel):
    """Pronunciation dictionary locator."""
    pronunciation_dictionary_id: str = Field(
        ...,
        description="ID of the pronunciation dictionary"
    )
    version_id: str = Field(
        ...,
        description="Version ID of the pronunciation dictionary"
    )


class ElevenLabsMultilingualV2QueryParameters(BaseModel):
    output_format: OutputFormat = Field(
        default=OutputFormat.MP3_44100_128,
        description="Output format of the generated audio",
    )
    
    enable_logging: bool = Field(
        default=True,
        description="When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.",
    )

class ElevenLabsMultilingualV2PathParameters(BaseModel):
    voice_id: str = Field(
        ...,
        description="ID of the voice to be used",
    )


class ElevenLabsMultilingualV2Input(BaseModel):
    """Input schema for ElevenLabs Multilingual V2 text-to-speech."""
    text: str = Field(
        ...,
        description="The text that will get converted into speech",
    )
    
    model_id: str = Field(
        default="eleven_multilingual_v2",
        description="Identifier of the model that will be used",
    )
    
    language_code: Optional[str] = Field(
        default=None,
        description="Language code (ISO 639-1) used to enforce a language for the model",
    )
    
    voice_settings: Optional[VoiceSettings] = Field(
        default=None,
        description="Voice settings overriding stored settings for the given voice",
    )
    
    pronunciation_dictionary_locators: Optional[List[PronunciationDictionaryLocator]] = Field(
        default=None,
        max_items=3,
        description="A list of pronunciation dictionary locators (id, version_id) to be applied to the text. They will be applied in order. You may have up to 3 locators per request",
    )
    
    seed: Optional[int] = Field(
        default=None,
        ge=0,
        le=4294967295,
        description="Seed for deterministic generation",
    )
    
    previous_text: Optional[str] = Field(
        default=None,
        description="The text that came before the text of the current request",
    )
    
    next_text: Optional[str] = Field(
        default=None,
        description="The text that comes after the text of the current request",
    )
    
    previous_request_ids: Optional[List[str]] = Field(
        default=None,
        max_items=3,
        description="A list of request_id of the samples that were generated before this generation",
    )
    
    next_request_ids: Optional[List[str]] = Field(
        default=None,
        max_items=3,
        description="A list of request_id of the samples that come after this generation",
    )
    
    apply_text_normalization: ApplyTextNormalization = Field(
        default=ApplyTextNormalization.OFF,
        description="This parameter controls text normalization with three modes: 'auto', 'on', and 'off'. When set to 'auto', the system will automatically decide whether to apply text normalization (e.g., spelling out numbers). With 'on', text normalization will always be applied, while with 'off', it will be skipped. Cannot be turned on for 'eleven_turbo_v2_5' or 'eleven_flash_v2_5' models.",
    )
    
    apply_language_text_normalization: bool = Field(
        default=False,
        description="Controls language text normalization for proper pronunciation",
    )
    


class ElevenLabsMultilingualV2Output(BaseModel):
    """Output schema for ElevenLabs Multilingual V2 text-to-speech."""
    # The output is binary data
    pass
