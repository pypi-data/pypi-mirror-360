from pydantic import BaseModel, Field
from enum import Enum

class VoiceIDEnum(str, Enum):
    """
    Available system voice IDs.
    """
    WISE_WOMAN = "Wise_Woman"
    FRIENDLY_PERSON = "Friendly_Person"
    INSPIRATIONAL_GIRL = "Inspirational_girl"
    DEEP_VOICE_MAN = "Deep_Voice_Man"
    CALM_WOMAN = "Calm_Woman"
    CASUAL_GUY = "Casual_Guy"
    LIVELY_GIRL = "Lively_Girl"
    PATIENT_MAN = "Patient_Man"
    YOUNG_KNIGHT = "Young_Knight"
    DETERMINED_MAN = "Determined_Man"
    LOVELY_GIRL = "Lovely_Girl"
    DECENT_BOY = "Decent_Boy"
    IMPOSING_MANNER = "Imposing_Manner"
    ELEGANT_MAN = "Elegant_Man"
    ABBESS = "Abbess"
    SWEET_GIRL_2 = "Sweet_Girl_2"
    EXUBERANT_GIRL = "Exuberant_Girl"

class BitrateEnum(int, Enum):
    """Bitrate for the generated speech"""
    B32000 = 32000
    B64000 = 64000
    B128000 = 128000
    B256000 = 256000


class ChannelEnum(str, Enum):
    """Number of audio channels"""
    MONO = "mono"
    STEREO = "stereo"


class EmotionEnum(str, Enum):
    """Speech emotion"""
    AUTO = "auto"
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    SURPRISED = "surprised"


class SampleRateEnum(int, Enum):
    """Sample rate for the generated speech"""
    S8000 = 8000
    S16000 = 16000
    S22050 = 22050
    S24000 = 24000
    S32000 = 32000
    S44100 = 44100


class LanguageBoostEnum(str, Enum):
    """Enhance recognition of specific languages and dialects"""
    NONE = "None"
    AUTOMATIC = "Automatic"
    CHINESE = "Chinese"
    CHINESE_YUE = "Chinese,Yue"
    ENGLISH = "English"
    ARABIC = "Arabic"
    RUSSIAN = "Russian"
    SPANISH = "Spanish"
    FRENCH = "French"
    PORTUGUESE = "Portuguese"
    GERMAN = "German"
    TURKISH = "Turkish"
    DUTCH = "Dutch"
    UKRAINIAN = "Ukrainian"
    VIETNAMESE = "Vietnamese"
    INDONESIAN = "Indonesian"
    JAPANESE = "Japanese"
    ITALIAN = "Italian"
    KOREAN = "Korean"
    THAI = "Thai"
    POLISH = "Polish"
    ROMANIAN = "Romanian"
    GREEK = "Greek"
    CZECH = "Czech"
    FINNISH = "Finnish"
    HINDI = "Hindi"


class MinimaxSpeechInput(BaseModel):
    """
    Input for the speech generation model.
    """
    text: str = Field(
        ...,
        title="Text",
        description="Text to convert to speech. Every character is 1 token. Maximum 5000 characters. Use <#x#> between words to control pause duration (0.01-99.99s).",
        json_schema_extra={"x-order": 0}
    )
    pitch: int = Field(
        default=0,
        ge=-12,
        le=12,
        title="Pitch",
        description="Speech pitch",
        json_schema_extra={"x-order": 4}
    )
    speed: float = Field(
        default=1,
        ge=0.5,
        le=2,
        title="Speed",
        description="Speech speed",
        json_schema_extra={"x-order": 2}
    )
    volume: float = Field(
        default=1,
        ge=0,
        le=10,
        title="Volume",
        description="Speech volume",
        json_schema_extra={"x-order": 3}
    )
    bitrate: BitrateEnum = Field(
        default=BitrateEnum.B128000,
        title="bitrate",
        description="Bitrate for the generated speech",
        json_schema_extra={"x-order": 8}
    )
    channel: ChannelEnum = Field(
        default=ChannelEnum.MONO,
        title="channel",
        description="Number of audio channels",
        json_schema_extra={"x-order": 9}
    )
    emotion: EmotionEnum = Field(
        default=EmotionEnum.AUTO,
        title="emotion",
        description="Speech emotion",
        json_schema_extra={"x-order": 5}
    )
    voice_id: VoiceIDEnum = Field(
        default=VoiceIDEnum.WISE_WOMAN,
        title="Voice Id",
        description="Desired voice ID. Use a voice ID you have trained (https://replicate.com/minimax/voice-cloning), or one of the following system voice IDs: Wise_Woman, Friendly_Person, Inspirational_girl, Deep_Voice_Man, Calm_Woman, Casual_Guy, Lively_Girl, Patient_Man, Young_Knight, Determined_Man, Lovely_Girl, Decent_Boy, Imposing_Manner, Elegant_Man, Abbess, Sweet_Girl_2, Exuberant_Girl",
        json_schema_extra={"x-order": 1}
    )
    sample_rate: SampleRateEnum = Field(
        default=SampleRateEnum.S32000,
        title="sample_rate",
        description="Sample rate for the generated speech",
        json_schema_extra={"x-order": 7}
    )
    language_boost: LanguageBoostEnum = Field(
        default=LanguageBoostEnum.NONE,
        title="language_boost",
        description="Enhance recognition of specific languages and dialects",
        json_schema_extra={"x-order": 10}
    )
    english_normalization: bool = Field(
        default=False,
        title="English Normalization",
        description="Enable English text normalization for better number reading (slightly increases latency)",
        json_schema_extra={"x-order": 6}
    )