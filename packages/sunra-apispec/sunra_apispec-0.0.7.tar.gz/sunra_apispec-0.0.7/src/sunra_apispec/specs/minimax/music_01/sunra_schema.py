# Schema for Text-to-music generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal

class TextToMusicInput(BaseModel):
    lyrics: str = Field(
        default="""
[intro]

Upload my heart to the digital sky
Algorithm love, you make me feel so high
Binary kisses, ones and zeros fly (fly)
Ooooh ooooh

[chorus]
Your neural network's got me feeling so alive
        """,
        description="Lyrics with optional formatting. You can use a newline to separate each line of lyrics. You can use two newlines to add a pause between lines. You can use double hash marks (##) at the beginning and end of the lyrics to add accompaniment. Maximum 350 to 400 characters.",
        json_schema_extra={"x-sr-order": 301},
        max_length=400
    )
    song_reference: HttpUrl | str = Field(
        default=None,
        description="Reference song, should contain music and vocals. Must be a .wav or .mp3 file longer than 15 seconds.",
        json_schema_extra={"x-sr-order": 302}
    )
    voice_reference: HttpUrl | str = Field(
        default=None,
        description="Voice reference. Must be a .wav or .mp3 file longer than 15 seconds. If only a voice reference is given, an a cappella vocal hum will be generated.",
        json_schema_extra={"x-sr-order": 303}
    )
    instrumental_reference: HttpUrl | str = Field(
        default=None,
        description="Instrumental reference. Must be a .wav or .mp3 file longer than 15 seconds. If only an instrumental reference is given, a track without vocals will be generated.",
        json_schema_extra={"x-sr-order": 304}
    )
    sample_rate: Literal[16000, 24000, 32000, 44100] = Field(
        default=44100,
        description="Sample rate for the generated music",
        json_schema_extra={"x-sr-order": 401}
    )
    bitrate: Literal[32000, 64000, 128000, 256000] = Field(
        default=256000,
        description="Bitrate for the generated music",
        json_schema_extra={"x-sr-order": 402}
    )
