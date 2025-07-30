from enum import Enum
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueueStatusStatus(Enum):
    """
    Represents the status of an item in the queue.
    """
    IN_QUEUE = "IN_QUEUE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class QueueStatus(BaseModel):
    """
    Represents the status of a request in the queue.
    """
    status: QueueStatusStatus
    request_id: str = Field(..., description="The request id.")
    response_url: Optional[str] = Field(None, description="The response url.")
    status_url: Optional[str] = Field(None, description="The status url.")
    cancel_url: Optional[str] = Field(None, description="The cancel url.")
    logs: Optional[Dict[str, Any]] = Field(None, description="The logs.")
    metrics: Optional[Dict[str, Any]] = Field(None, description="The metrics.")
    queue_position: Optional[int] = Field(None, description="The queue position.")


class File(BaseModel):
    """
    Represents a file with its URL, size, name, content type, and optional binary data.
    """
    url: str = Field(..., description="The URL where the file can be downloaded from.", title="Url")
    file_size: Optional[int] = Field(
        None, description="The size of the file in bytes.", examples=[4404019], title="File Size"
    )
    file_name: Optional[str] = Field(
        None, description="The name of the file. It will be auto-generated if not provided.", examples=["z9RV14K95DvU.png"], title="File Name"
    )
    content_type: Optional[str] = Field(
        None, description="The mime type of the file.", examples=["image/png"], title="Content Type"
    )
    file_data: Optional[str] = Field(None, description="File data", format="binary", title="File Data")
    

class AceStepOutput(BaseModel):
    """
    Represents the output of an AceStep audio generation process.
    """
    audio: File = Field(..., description="The generated audio file.", title="Audio")
    seed: int = Field(..., description="The random seed used for the generation process.", examples=[42], title="Seed")
    tags: str = Field(
        ...,
        examples=["lofi, hiphop, drum and bass, trap, chill"],
        description="The genre tags used in the generation process.",
        title="Tags",
    )
    lyrics: str = Field(
        ..., examples=["[inst]"], description="The lyrics used in the generation process.", title="Lyrics"
    )

    
    
class AceStepTextToMusicInput(BaseModel):
    """
    Text to Music
    Represents the input parameters for an AceStep audio generation process.
    """
    number_of_steps: int = Field(
        27,
        ge=3,
        le=60,
        description="Number of steps to generate the audio.",
        examples=[27],
        title="Number Of Steps",
    )
    duration: float = Field(
        60,
        ge=5,
        le=240,
        description="The duration of the generated audio in seconds.",
        title="Duration",
    )
    tags: str = Field(
        ...,
        examples=["lofi, hiphop, drum and bass, trap, chill"],
        description="Comma-separated list of genre tags to control the style of the generated audio.",
        title="Tags",
    )
    minimum_guidance_scale: float = Field(
        3,
        ge=0,
        le=200,
        description="Minimum guidance scale for the generation after the decay.",
        examples=[3],
        title="Minimum Guidance Scale",
    )
    lyrics: str = Field(
        "",
        description="Lyrics to be sung in the audio. If not provided or if [inst] or [instrumental] is the content of this field, no lyrics will be sung. Use control structures like [verse], [chorus] and [bridge] to control the structure of the song.",
        title="Lyrics",
    )
    tag_guidance_scale: float = Field(
        5,
        ge=0,
        le=10,
        description="Tag guidance scale for the generation.",
        examples=[5],
        title="Tag Guidance Scale",
    )
    scheduler: Literal["euler", "heun"] = Field(
        "euler",
        examples=["euler"],
        description="Scheduler to use for the generation process.",
        title="Scheduler",
    )
    guidance_scale: float = Field(
        15,
        ge=0,
        le=200,
        description="Guidance scale for the generation.",
        examples=[15],
        title="Guidance Scale",
    )
    guidance_type: Literal["cfg", "apg", "cfg_star"] = Field(
        "apg",
        examples=["apg"],
        description="Type of CFG to use for the generation process.",
        title="Guidance Type",
    )
    lyric_guidance_scale: float = Field(
        1.5,
        ge=0,
        le=10,
        description="Lyric guidance scale for the generation.",
        examples=[1.5],
        title="Lyric Guidance Scale",
    )
    guidance_interval: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Guidance interval for the generation. 0.5 means only apply guidance in the middle steps (0.25 * infer_steps to 0.75 * infer_steps)",
        examples=[0.5],
        title="Guidance Interval",
    )
    guidance_interval_decay: float = Field(
        0,
        ge=0,
        le=1,
        description="Guidance interval decay for the generation. Guidance scale will decay from guidance_scale to min_guidance_scale in the interval. 0.0 means no decay.",
        examples=[0],
        title="Guidance Interval Decay",
    )
    seed: Optional[int] = Field(
        None, description="Random seed for reproducibility. If not provided, a random seed will be used.", title="Seed"
    )
    granularity_scale: int = Field(
        10,
        ge=-100,
        le=100,
        description="Granularity scale for the generation process. Higher values can reduce artifacts.",
        examples=[10],
        title="Granularity Scale",
    )





class AceStepAudioToAudioInput(BaseModel):
    """
    Music Editing
    Represents the input parameters for an AceStep audio-to-audio generation process.
    """
    tags: str = Field(
        ...,
        examples=["lofi, hiphop, drum and bass, trap, chill"],
        description="Comma-separated list of genre tags to control the style of the generated audio.",
        title="Tags",
    )
    audio_url: str = Field(
        ...,
        examples=["https://storage.googleapis.com/falserverless/example_inputs/ace-step-audio-to-audio.wav"],
        description="URL of the audio file to be outpainted.",
        title="Audio Url",
    )
    original_tags: str = Field(
        ...,
        examples=["lofi, hiphop, drum and bass, trap, chill"],
        description="Original tags of the audio file.",
        title="Original Tags",
    )
    number_of_steps: int = Field(
        27,
        ge=3,
        le=60,
        description="Number of steps to generate the audio.",
        examples=[27],
        title="Number Of Steps",
    )
    minimum_guidance_scale: float = Field(
        3,
        ge=0,
        le=200,
        description="Minimum guidance scale for the generation after the decay.",
        examples=[3],
        title="Minimum Guidance Scale",
    )
    lyrics: str = Field(
        "",
        description="Lyrics to be sung in the audio. If not provided or if [inst] or [instrumental] is the content of this field, no lyrics will be sung. Use control structures like [verse], [chorus] and [bridge] to control the structure of the song.",
        title="Lyrics",
    )
    tag_guidance_scale: float = Field(
        5,
        ge=0,
        le=10,
        description="Tag guidance scale for the generation.",
        examples=[5],
        title="Tag Guidance Scale",
    )
    original_lyrics: str = Field(
        "", examples=[""], description="Original lyrics of the audio file.", title="Original Lyrics"
    )
    scheduler: Literal["euler", "heun"] = Field(
        "euler",
        examples=["euler"],
        description="Scheduler to use for the generation process.",
        title="Scheduler",
    )
    guidance_scale: float = Field(
        15,
        ge=0,
        le=200,
        description="Guidance scale for the generation.",
        examples=[15],
        title="Guidance Scale",
    )
    guidance_type: Literal["cfg", "apg", "cfg_star"] = Field(
        "apg",
        examples=["apg"],
        description="Type of CFG to use for the generation process.",
        title="Guidance Type",
    )
    lyric_guidance_scale: float = Field(
        1.5,
        ge=0,
        le=10,
        description="Lyric guidance scale for the generation.",
        examples=[1.5],
        title="Lyric Guidance Scale",
    )
    guidance_interval: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Guidance interval for the generation. 0.5 means only apply guidance in the middle steps (0.25 * infer_steps to 0.75 * infer_steps)",
        examples=[0.5],
        title="Guidance Interval",
    )
    edit_mode: Literal["lyrics", "remix"] = Field(
        "remix",
        examples=["remix"],
        description="Whether to edit the lyrics only or remix the audio.",
        title="Edit Mode",
    )
    guidance_interval_decay: float = Field(
        0,
        ge=0,
        le=1,
        description="Guidance interval decay for the generation. Guidance scale will decay from guidance_scale to min_guidance_scale in the interval. 0.0 means no decay.",
        examples=[0],
        title="Guidance Interval Decay",
    )
    seed: Optional[int] = Field(
        None, description="Random seed for reproducibility. If not provided, a random seed will be used.", title="Seed"
    )
    granularity_scale: int = Field(
        10,
        ge=-100,
        le=100,
        description="Granularity scale for the generation process. Higher values can reduce artifacts.",
        examples=[10],
        title="Granularity Scale",
    )
    original_seed: Optional[int] = Field(None, description="Original seed of the audio file.", title="Original Seed")


class AceStepAudioOutpaintInput(BaseModel):
    """
    Music Extending
    Represents the input parameters for an AceStep audio outpainting process.
    """
    tags: str = Field(
        ...,
        examples=["lofi, hiphop, drum and bass, trap, chill"],
        description="Comma-separated list of genre tags to control the style of the generated audio.",
        title="Tags",
    )
    audio_url: str = Field(
        ...,
        examples=["https://storage.googleapis.com/falserverless/example_inputs/ace-step-audio-to-audio.wav"],
        description="URL of the audio file to be outpainted.",
        title="Audio Url",
    )
    number_of_steps: int = Field(
        27,
        ge=3,
        le=60,
        description="Number of steps to generate the audio.",
        examples=[27],
        title="Number Of Steps",
    )
    minimum_guidance_scale: float = Field(
        3,
        ge=0,
        le=200,
        description="Minimum guidance scale for the generation after the decay.",
        examples=[3],
        title="Minimum Guidance Scale",
    )
    extend_after_duration: float = Field(
        30,
        ge=0,
        le=240,
        description="Duration in seconds to extend the audio from the end.",
        examples=[30],
        title="Extend After Duration",
    )
    lyrics: str = Field(
        "",
        description="Lyrics to be sung in the audio. If not provided or if [inst] or [instrumental] is the content of this field, no lyrics will be sung. Use control structures like [verse], [chorus] and [bridge] to control the structure of the song.",
        title="Lyrics",
    )
    tag_guidance_scale: float = Field(
        5,
        ge=0,
        le=10,
        description="Tag guidance scale for the generation.",
        examples=[5],
        title="Tag Guidance Scale",
    )
    scheduler: Literal["euler", "heun"] = Field(
        "euler",
        examples=["euler"],
        description="Scheduler to use for the generation process.",
        title="Scheduler",
    )
    extend_before_duration: float = Field(
        0,
        ge=0,
        le=240,
        description="Duration in seconds to extend the audio from the start.",
        examples=[0],
        title="Extend Before Duration",
    )
    guidance_type: Literal["cfg", "apg", "cfg_star"] = Field(
        "apg",
        examples=["apg"],
        description="Type of CFG to use for the generation process.",
        title="Guidance Type",
    )
    guidance_scale: float = Field(
        15,
        ge=0,
        le=200,
        description="Guidance scale for the generation.",
        examples=[15],
        title="Guidance Scale",
    )
    lyric_guidance_scale: float = Field(
        1.5,
        ge=0,
        le=10,
        description="Lyric guidance scale for the generation.",
        examples=[1.5],
        title="Lyric Guidance Scale",
    )
    guidance_interval: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Guidance interval for the generation. 0.5 means only apply guidance in the middle steps (0.25 * infer_steps to 0.75 * infer_steps)",
        examples=[0.5],
        title="Guidance Interval",
    )
    guidance_interval_decay: float = Field(
        0,
        ge=0,
        le=1,
        description="Guidance interval decay for the generation. Guidance scale will decay from guidance_scale to min_guidance_scale in the interval. 0.0 means no decay.",
        examples=[0],
        title="Guidance Interval Decay",
    )
    seed: Optional[int] = Field(
        None, description="Random seed for reproducibility. If not provided, a random seed will be used.", title="Seed"
    )
    granularity_scale: int = Field(
        10,
        ge=-100,
        le=100,
        description="Granularity scale for the generation process. Higher values can reduce artifacts.",
        examples=[10],
        title="Granularity Scale",
    )


class AceStepAudioInpaintInput(BaseModel):
    """
    Music Inpainting
    Represents the input parameters for an AceStep audio inpainting process.
    """
    number_of_steps: int = Field(
        27,
        ge=3,
        le=60,
        description="Number of steps to generate the audio.",
        examples=[27],
        title="Number Of Steps",
    )
    start_time: float = Field(
        0,
        ge=0,
        le=240,
        description="start time in seconds for the inpainting process.",
        examples=[0],
        title="Start Time",
    )
    tags: str = Field(
        ...,
        examples=["lofi, hiphop, drum and bass, trap, chill"],
        description="Comma-separated list of genre tags to control the style of the generated audio.",
        title="Tags",
    )
    minimum_guidance_scale: float = Field(
        3,
        ge=0,
        le=200,
        description="Minimum guidance scale for the generation after the decay.",
        examples=[3],
        title="Minimum Guidance Scale",
    )
    lyrics: str = Field(
        "",
        description="Lyrics to be sung in the audio. If not provided or if [inst] or [instrumental] is the content of this field, no lyrics will be sung. Use control structures like [verse], [chorus] and [bridge] to control the structure of the song.",
        title="Lyrics",
    )
    end_time_relative_to: Literal["start", "end"] = Field(
        "start",
        examples=["start"],
        description="Whether the end time is relative to the start or end of the audio.",
        title="End Time Relative To",
    )
    tag_guidance_scale: float = Field(
        5,
        ge=0,
        le=10,
        description="Tag guidance scale for the generation.",
        examples=[5],
        title="Tag Guidance Scale",
    )
    scheduler: Literal["euler", "heun"] = Field(
        "euler",
        examples=["euler"],
        description="Scheduler to use for the generation process.",
        title="Scheduler",
    )
    end_time: float = Field(
        30,
        ge=0,
        le=240,
        description="end time in seconds for the inpainting process.",
        examples=[30],
        title="End Time",
    )
    guidance_type: Literal["cfg", "apg", "cfg_star"] = Field(
        "apg",
        examples=["apg"],
        description="Type of CFG to use for the generation process.",
        title="Guidance Type",
    )
    guidance_scale: float = Field(
        15,
        ge=0,
        le=200,
        description="Guidance scale for the generation.",
        examples=[15],
        title="Guidance Scale",
    )
    lyric_guidance_scale: float = Field(
        1.5,
        ge=0,
        le=10,
        description="Lyric guidance scale for the generation.",
        examples=[1.5],
        title="Lyric Guidance Scale",
    )
    guidance_interval: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Guidance interval for the generation. 0.5 means only apply guidance in the middle steps (0.25 * infer_steps to 0.75 * infer_steps)",
        examples=[0.5],
        title="Guidance Interval",
    )
    variance: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Variance for the inpainting process. Higher values can lead to more diverse results.",
        examples=[0.5],
        title="Variance",
    )
    guidance_interval_decay: float = Field(
        0,
        ge=0,
        le=1,
        description="Guidance interval decay for the generation. Guidance scale will decay from guidance_scale to min_guidance_scale in the interval. 0.0 means no decay.",
        examples=[0],
        title="Guidance Interval Decay",
    )
    start_time_relative_to: Literal["start", "end"] = Field(
        "start",
        examples=["start"],
        description="Whether the start time is relative to the start or end of the audio.",
        title="Start Time Relative To",
    )
    audio_url: str = Field(
        ...,
        examples=["https://storage.googleapis.com/falserverless/example_inputs/ace-step-audio-to-audio.wav"],
        description="URL of the audio file to be inpainted.",
        title="Audio Url",
    )
    seed: Optional[int] = Field(
        None, description="Random seed for reproducibility. If not provided, a random seed will be used.", title="Seed"
    )
    granularity_scale: int = Field(
        10,
        ge=-100,
        le=100,
        description="Granularity scale for the generation process. Higher values can reduce artifacts.",
        examples=[10],
        title="Granularity Scale",
    )