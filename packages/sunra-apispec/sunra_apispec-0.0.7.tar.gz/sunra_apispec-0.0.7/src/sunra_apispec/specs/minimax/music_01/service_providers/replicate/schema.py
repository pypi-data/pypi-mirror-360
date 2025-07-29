# Schema for MiniMax Music Generation
from pydantic import BaseModel, Field
from typing import Optional, Literal

class MinimaxMusicInput(BaseModel):
    """
    Input Schema for Replicate's Minimax text to music
    """
    lyrics: str = Field(
        default="",
        description="Lyrics with optional formatting. You can use a newline to separate each line of lyrics. You can use two newlines to add a pause between lines. You can use double hash marks (##) at the beginning and end of the lyrics to add accompaniment. Maximum 350 to 400 characters.",
        json_schema_extra={"x-order": 0},
        max_length=400
    )
    song_file: Optional[str] = Field(
        default=None,
        description="Reference song, should contain music and vocals. Must be a .wav or .mp3 file longer than 15 seconds.",
        json_schema_extra={"x-order": 1}
    )
    voice_file: Optional[str] = Field(
        default=None,
        description="Voice reference. Must be a .wav or .mp3 file longer than 15 seconds. If only a voice reference is given, an a cappella vocal hum will be generated.",
        json_schema_extra={"x-order": 2}
    )
    instrumental_file: Optional[str] = Field(
        default=None,
        description="Instrumental reference. Must be a .wav or .mp3 file longer than 15 seconds. If only an instrumental reference is given, a track without vocals will be generated.",
        json_schema_extra={"x-order": 3}
    )
    voice_id: Optional[str] = Field(
        default=None,
        description="Reuse a previously uploaded voice ID",
        json_schema_extra={"x-order": 4}
    )
    instrumental_id: Optional[str] = Field(
        default=None,
        description="Reuse a previously uploaded instrumental ID",
        json_schema_extra={"x-order": 5}
    )
    sample_rate: Literal[16000, 24000, 32000, 44100] = Field(
        default=44100,
        description="Sample rate for the generated music",
        json_schema_extra={"x-order": 6}
    )
    bitrate: Literal[32000, 64000, 128000, 256000] = Field(
        default=256000,
        description="Bitrate for the generated music",
        json_schema_extra={"x-order": 7}
    )