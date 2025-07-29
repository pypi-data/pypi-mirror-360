from pydantic import BaseModel, Field
from pydantic import HttpUrl

class SpeechToTextInput(BaseModel):
    audio: HttpUrl | str = Field(
        ...,
        title="Audio",
        description="The audio file object (not file name) to transcribe, in one of these formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.",
        json_schema_extra={"x-sr-order": 301}
    )

class GPT4oTranscribeOutput(BaseModel):
    text: str
    input_token_count: int
    output_token_count: int
