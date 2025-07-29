from pydantic import BaseModel, Field
from typing import Literal
from sunra_apispec.base.output_schema import AudioOutput


class TextToSpeechInput(BaseModel):
    text: str = Field(
        ...,
        title="Text",
        description="Text to convert to speech. Every character is 1 token. Maximum 5000 characters. Use <#x#> between words to control pause duration (0.01-99.99s).",
        json_schema_extra={"x-sr-order": 201}
    )
    voice_id: Literal[
        "Wise_Woman", "Friendly_Person", "Inspirational_girl", "Deep_Voice_Man", "Calm_Woman",
        "Casual_Guy", "Lively_Girl", "Patient_Man", "Young_Knight", "Determined_Man",
        "Lovely_Girl", "Decent_Boy", "Imposing_Manner", "Elegant_Man", "Abbess",
        "Sweet_Girl_2", "Exuberant_Girl"
    ] = Field(
        default="Wise_Woman",
        title="Voice Id",
        description="Desired voice ID. Use a voice ID you have trained (https://replicate.com/minimax/voice-cloning), or one of the following system voice IDs: Wise_Woman, Friendly_Person, Inspirational_girl, Deep_Voice_Man, Calm_Woman, Casual_Guy, Lively_Girl, Patient_Man, Young_Knight, Determined_Man, Lovely_Girl, Decent_Boy, Imposing_Manner, Elegant_Man, Abbess, Sweet_Girl_2, Exuberant_Girl",
        json_schema_extra={"x-sr-order": 301}
    )
    speed: float = Field(
        default=1,
        ge=0.5,
        le=2,
        multiple_of=0.01,
        title="Speed",
        description="Speech speed",
        json_schema_extra={"x-sr-order": 401}
    )
    volume: float = Field(
        default=1,
        ge=0,
        le=10,
        multiple_of=0.1,
        title="Volume",
        description="Speech volume",
        json_schema_extra={"x-sr-order": 402}
    )
    pitch: int = Field(
        default=0,
        ge=-12,
        le=12,
        multiple_of=1,
        title="Pitch",
        description="Speech pitch",
        json_schema_extra={"x-sr-order": 403}
    )
    emotion: Literal[
        "auto", "neutral", "happy", "sad", "angry", "fearful", "disgusted", "surprised"
    ] = Field(
        default="auto",
        title="emotion",
        description="Speech emotion",
        json_schema_extra={"x-sr-order": 404}
    )
    english_normalization: bool = Field(
        default=False,
        title="English Normalization",
        description="Enable English text normalization for better number reading (slightly increases latency)",
        json_schema_extra={"x-sr-order": 405}
    )
    sample_rate: Literal[
        8000, 16000, 22050, 24000, 32000, 44100
    ] = Field(
        default=32000,
        title="sample_rate",
        description="Sample rate for the generated speech",
        json_schema_extra={"x-sr-order": 406}
    )
    bitrate: Literal[
        32000, 64000, 128000, 256000
    ] = Field(
        default=128000,
        title="bitrate",
        description="Bitrate for the generated speech",
        json_schema_extra={"x-sr-order": 407}
    )
    channel: Literal[
        "mono", "stereo"
    ] = Field(
        default="mono",
        title="channel",
        description="Number of audio channels",
        json_schema_extra={"x-sr-order": 408}
    )
    language_boost: Literal[
        "None", "Automatic", "Chinese", "Chinese,Yue", "English", "Arabic", "Russian",
        "Spanish", "French", "Portuguese", "German", "Turkish", "Dutch", "Ukrainian",
        "Vietnamese", "Indonesian", "Japanese", "Italian", "Korean", "Thai", "Polish",
        "Romanian", "Greek", "Czech", "Finnish", "Hindi"
    ] = Field(
        default="None",
        title="language_boost",
        description="Enhance recognition of specific languages and dialects",
        json_schema_extra={"x-sr-order": 409}
    )


class MinimaxSpeech02TurboOutput(AudioOutput):
    input_tokens: int = Field(
        ...,
        description="Number of input tokens",
    )
    predict_time: float = Field(
        ...,
        description="Time taken to generate the audio",
    )
