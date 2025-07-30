from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Union


class ChunkingStrategyServerVad(BaseModel):
    type: Literal["server_vad"] = Field(
        ...,
        description="The chunking strategy type"
    )
    vad_detection_threshold: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Voice activity detection threshold"
    )


class OpenAITranscribeInput(BaseModel):
    file: str = Field(
        ...,
        description="The audio file object (not file name) to transcribe, in one of these formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm."
    )
    
    model: Literal["gpt-4o-transcribe", "gpt-4o-mini-transcribe", "whisper-1"] = Field(
        default="gpt-4o-transcribe",
        description="ID of the model to use. The options are gpt-4o-transcribe, gpt-4o-mini-transcribe, and whisper-1."
    )
    
    chunking_strategy: Optional[Union[Literal["auto"], ChunkingStrategyServerVad]] = Field(
        default=None,
        description="Controls how the audio is cut into chunks."
    )
    
    include: Optional[List[Literal["logprobs"]]] = Field(
        default=None,
        description="Additional information to include in the transcription response."
    )
    
    language: Optional[str] = Field(
        default=None,
        description="The language of the input audio. Supplying the input language in ISO-639-1 format will improve accuracy and latency."
    )
    
    prompt: Optional[str] = Field(
        default=None,
        description="An optional text to guide the model's style or continue a previous audio segment."
    )
    
    response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] = Field(
        default="json",
        description="The format of the output, in one of these options: json, text, srt, verbose_json, or vtt."
    )
    
    stream: Optional[bool] = Field(
        default=False,
        description="If set to true, the model response data will be streamed to the client."
    )
    
    temperature: Optional[float] = Field(
        default=0,
        ge=0,
        le=1,
        description="The sampling temperature, between 0 and 1."
    )
    
    timestamp_granularities: Optional[List[Literal["word", "segment"]]] = Field(
        default=["segment"],
        description="The timestamp granularities to populate for this transcription."
    )


class LogProb(BaseModel):
    bytes: List[int] = Field(..., description="The bytes of the token.")
    logprob: float = Field(..., description="The log probability of the token.")
    token: str = Field(..., description="The token in the transcription.")


class Word(BaseModel):
    word: str = Field(..., description="The word.")
    start: float = Field(..., description="Start timestamp.")
    end: float = Field(..., description="End timestamp.")


class Segment(BaseModel):
    id: int = Field(..., description="Segment ID.")
    seek: float = Field(..., description="Seek position.")
    start: float = Field(..., description="Start timestamp.")
    end: float = Field(..., description="End timestamp.")
    text: str = Field(..., description="Segment text.")
    tokens: List[int] = Field(..., description="Token IDs.")
    temperature: float = Field(..., description="Temperature used.")
    avg_logprob: float = Field(..., description="Average log probability.")
    compression_ratio: float = Field(..., description="Compression ratio.")
    no_speech_prob: float = Field(..., description="No speech probability.")


class OpenAITranscribeOutput(BaseModel):
    text: str = Field(..., description="The transcribed text.")
    logprobs: Optional[List[LogProb]] = Field(
        default=None,
        description="The log probabilities of the tokens in the transcription."
    )
    words: Optional[List[Word]] = Field(
        default=None,
        description="Extracted words and their corresponding timestamps."
    )
    segments: Optional[List[Segment]] = Field(
        default=None,
        description="Segments of the transcription with timestamps."
    )
