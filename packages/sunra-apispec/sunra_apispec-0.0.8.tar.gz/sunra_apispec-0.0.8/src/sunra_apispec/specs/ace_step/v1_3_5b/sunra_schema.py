from typing import Literal
from pydantic import BaseModel, Field, HttpUrl

from sunra_apispec.base.output_schema import AudioOutput, SunraFile


class BaseAudioGenerationInput(BaseModel):
    """
    Base class for audio generation inputs, containing common parameters.
    """
    number_of_steps: int = Field(
        30,
        ge=5,
        le=60,
        multiple_of=1,
        description="Number of steps to generate the audio.",
        title="Number Of Steps",
        json_schema_extra={"x-sr-order": 410}
    )
    scheduler: Literal["euler", "heun"] = Field(
        "euler",
        description="Scheduler to use for the generation process.",
        title="Scheduler",
        json_schema_extra={"x-sr-order": 411}
    )
    guidance_type: Literal["cfg", "apg", "cfg_star"] = Field(
        "apg",
        description="Type of CFG to use for the generation process.",
        title="Guidance Type",
        json_schema_extra={"x-sr-order": 412}
    )
    granularity_scale: float = Field(
        10,
        ge=-100,
        le=100,
        multiple_of=1,
        description="Granularity scale for the generation process. Higher values can reduce artifacts.",
        title="Granularity Scale",
        json_schema_extra={"x-sr-order": 413}
    )
    guidance_interval: float = Field(
        0.5,
        ge=0,
        le=1,
        multiple_of=0.1,
        description="Guidance interval for the generation. 0.5 means only apply guidance in the middle steps (0.25 * infer_steps to 0.75 * infer_steps)",
        title="Guidance Interval",
        json_schema_extra={"x-sr-order": 414}
    )
    guidance_interval_decay: float = Field(
        0,
        ge=0,
        le=1,
        multiple_of=0.1,
        description="Guidance interval decay for the generation. Guidance scale will decay from guidance_scale to min_guidance_scale in the interval. 0.0 means no decay.",
        title="Guidance Interval Decay",
        json_schema_extra={"x-sr-order": 415}
    )
    guidance_scale: float = Field(
        15,
        ge=0,
        le=200,
        multiple_of=1,
        description="Guidance scale for the generation.",
        title="Guidance Scale",
        json_schema_extra={"x-sr-order": 416}
    )
    minimum_guidance_scale: float = Field(
        3,
        ge=0,
        le=200,
        multiple_of=1,
        description="Minimum guidance scale for the generation after the decay.",
        title="Minimum Guidance Scale",
        json_schema_extra={"x-sr-order": 417}
    )
    tag_guidance_scale: float = Field(
        5,
        ge=0,
        le=10,
        multiple_of=0.1,
        description="Tag guidance scale for the generation.",
        title="Tag Guidance Scale",
        json_schema_extra={"x-sr-order": 418}
    )
    lyric_guidance_scale: float = Field(
        1.5,
        ge=0,
        le=10,
        multiple_of=0.1,
        description="Lyric guidance scale for the generation.",
        title="Lyric Guidance Scale",
        json_schema_extra={"x-sr-order": 419}
    )

class TextToMusicInput(BaseAudioGenerationInput):
    """
    Text to Music
    Represents the input parameters for controlling the AceStep audio generation process.
    """
    tags: str = Field(
        ...,
        examples=["funk, pop, soul, rock, melodic, guitar, drums, bass, keyboard, percussion, 105 BPM, energetic, upbeat, groovy, vibrant, dynamic"],
        description="Text prompts to guide music generation, support tags, descriptions, and scenes. Use commas to separate different tags. e.g., 'epic,cinematic'",
        title="Tags",
        json_schema_extra={"x-sr-order": 301}
    )
    lyrics: str = Field(
        None,
        examples=["""[verse]Neon lights they flicker bright City hums in dead of night
                Rhythms pulse through concrete veins
                Lost in echoes of refrains

                [verse]
                Bassline groovin' in my chest
                Heartbeats match the city's zest
                Electric whispers fill the air
                Synthesized dreams everywhere

                [chorus]
                Turn it up and let it flow
                Feel the fire let it grow
                In this rhythm we belong
                Hear the night sing out our song

                [verse]
                Guitar strings they start to weep
                Wake the soul from silent sleep
                Every note a story told
                In this night we’re bold and gold

                [bridge]
                Voices blend in harmony
                Lost in pure cacophony
                Timeless echoes timeless cries
                Soulful shouts beneath the skies

                [verse]
                Keyboard dances on the keys
                Melodies on evening breeze
                Catch the tune and hold it tight
                In this moment we take flight"""],
        description="Lyrics to music. Use [verse], [chorus], and [bridge] to separate different parts of the lyrics. Use [instrumental] or [inst] to generate instrumental music",
        title="Lyrics",
        json_schema_extra={"x-sr-order": 302}
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        description="Random seed for reproducibility. If not provided, a random seed will be used.",
        title="Seed",
        json_schema_extra={"x-sr-order": 304}
    )
    duration: float = Field(
        20,
        ge=5,
        le=240,
        multiple_of=1,
        description="Duration of the generated audio in seconds",
        title="Duration",
        json_schema_extra={"x-sr-order": 401}
    )


class AudioToAudioInput(BaseAudioGenerationInput):
    """
    Music Editing
    Represents the input parameters for the AceStep audio-to-audio manipulation, including tags, audio URL, and guidance parameters.
    """
    audio: HttpUrl | str = Field(
        ...,
        description="URL of the audio file to be edited.",
        title="Audio Url",
        json_schema_extra={"x-sr-order": 301}
    )
    edit_mode: Literal["lyrics", "remix"] = Field(
        "remix",
        description="Whether to edit the lyrics only or remix the audio.",
        title="Edit Mode",
        json_schema_extra={"x-sr-order": 302}
    )
    original_tags: str = Field(
        "lofi, hiphop, drum and bass, trap, chill",
        description="Text prompts to guide music generation, support tags, descriptions, and scenes. Use commas to separate different tags.",
        title="Original Tags",
        json_schema_extra={"x-sr-order": 303}
    )
    original_lyrics: str = Field(
        "",
        description="Original lyrics of the audio file.",
        title="Original Lyrics",
        json_schema_extra={"x-sr-order": 304}
    )
    tags: str = Field(
        ...,
        examples=["lofi, hiphop, drum and bass, trap, chill"],
        description="Text prompts to guide music generation, support tags, descriptions, and scenes. Use commas to separate different tags. e.g., 'epic,cinematic'",
        title="Tags",
        json_schema_extra={"x-sr-order": 305}
    )
    lyrics: str = Field(
        "",
        description="""Lyrics to be sung in the audio.
                      If not provided or if [inst] or [instrumental] is the content of this field,
                      no lyrics will be sung. Use control structures like [verse],
                      [chorus] and [bridge] to control the structure of the song.""",
        title="Lyrics",
        json_schema_extra={"x-sr-order": 306}
    )
    original_seed: int = Field(
        None,
        ge=0,
        le=2147483647,
        description="Original seed of the audio file.",
        json_schema_extra={"x-sr-order": 308}
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        description="Random seed for reproducibility. If not provided, a random seed will be used.",
        json_schema_extra={"x-sr-order": 309}
    )



class AudioOutpaintInput(BaseAudioGenerationInput):
    """
    Music Extending
    Represents the input parameters for outpainting an audio file using AceStep, extending it before or after its original duration.
    """
    audio: HttpUrl | str = Field(
        ...,
        description="URL of the audio file to be outpainted.",
        title="Audio Url",
        json_schema_extra={"x-sr-order": 301}
    )
    extend_duration_before_start: int = Field(
        0,
        ge=0,
        le=240,
        multiple_of=1,
        description="Duration in seconds to extend the audio before the start.",
        title="Extend Before Duration",
        json_schema_extra={"x-sr-order": 302}
    )
    extend_durtion_after_end: int = Field(
        30,
        ge=0,
        le=240,
        multiple_of=1,
        description="Duration in seconds to extend the audio after the end. ",
        title="Extend After Duration",
        json_schema_extra={"x-sr-order": 303}
    )
    tags: str = Field(
        ...,
        examples=["lofi, hiphop, drum and bass, trap, chill"],
        description="Text prompts to guide music generation, support tags, descriptions, and scenes. Use commas to separate different tags. e.g., 'epic,cinematic'",
        title="Tags",
        json_schema_extra={"x-sr-order": 304}
    )
    lyrics: str = Field(
        "",
        description="Lyrics to be sung in the audio. If not provided or if [inst] or [instrumental] is the content of this field, no lyrics will be sung. Use control structures like [verse], [chorus] and [bridge] to control the structure of the song. ",
        title="Lyrics",
        json_schema_extra={"x-sr-order": 305}
    )

    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        description="Random seed for reproducibility. If not provided, a random seed will be used.",
        json_schema_extra={"x-sr-order": 401}
    )



class AudioInpaintInput(BaseAudioGenerationInput):
    """
    Music Inpainting
    Represents the input parameters for inpainting an audio file using AceStep, filling a specific time range within the audio.
    """
    audio: HttpUrl | str = Field(
        ...,
        description="URL of the audio file to be inpainted.",
        title="Audio Url",
        json_schema_extra={"x-sr-order": 301}
    )
    start_time_relative_to: Literal["start", "end"] = Field(
        "start",
        description="Whether the start time is relative to the start or end of the audio.",
        title="Start Time Relative To",
        json_schema_extra={"x-sr-order": 302}
    )
    start_time: int = Field(
        0,
        ge=0,
        le=240,
        multiple_of=1,
        description="start time in seconds for the inpainting process.",
        title="Start Time",
        json_schema_extra={"x-sr-order": 303}
    )
    end_time_relative_to: Literal["start", "end"] = Field(
        "start",
        description="Whether the end time is relative to the start or end of the audio.",
        title="End Time Relative To",
        json_schema_extra={"x-sr-order": 304}
    )
    end_time: int = Field(
        30,
        ge=0,
        le=240,
        multiple_of=1,
        description="end time in seconds for the inpainting process.",
        title="End Time",
        json_schema_extra={"x-sr-order": 305}
    )
    tags: str = Field(
        ...,
        examples=["lofi, hiphop, drum and bass, trap, chill"],
        description="Text prompts to guide music generation, support tags, descriptions, and scenes. Use commas to separate different tags. e.g., 'epic,cinematic'",
        title="Tags",
        json_schema_extra={"x-sr-order": 306}
    )
    lyrics: str = Field(
        "",
        description="Lyrics to be sung in the audio. If not provided or if [inst] or [instrumental] is the content of this field, no lyrics will be sung. Use control structures like [verse], [chorus] and [bridge] to control the structure of the song.",
        title="Lyrics",
        json_schema_extra={"x-sr-order": 307}
    )
    variance: float = Field(
        0.5,
        ge=0,
        le=1,
        multiple_of=0.1,
        description="Variance for the inpainting process. Higher values can lead to more diverse results.",
        title="Variance",
        json_schema_extra={"x-sr-order": 401}
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        description="Random seed for reproducibility. If not provided, a random seed will be used.",
        title="Seed",
        json_schema_extra={"x-sr-order": 403}
    )


class AceStepV135BAudioFile(SunraFile):
    duration: int = Field(
        ...,
        description="Duration of the audio in seconds",
    )

class AceStepV135BOutput(AudioOutput):
    audio: AceStepV135BAudioFile
