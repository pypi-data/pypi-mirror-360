# Schema for video inpainting
from pydantic import BaseModel, Field, HttpUrl
from sunra_apispec.base.output_schema import VideoOutput


class VideoInpaintingInput(BaseModel):
    """Input model for video inpainting."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Prompt for inpainting the masked area.",
    )

    number_of_steps: int = Field(
        default=50,
        ge=20,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 204},
        description="Number of sampling steps.",
    )

    guidance_scale: float = Field(
        default=5.0,
        ge=1.0,
        le=15.0,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 205},
        description="Guidance scale for prompt adherence.",
    )

    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 206},
        description="Random seed for reproducibility.",
    )
    
    
    video: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Original video to be inpainted.",
    )
    
    mask_video: HttpUrl | str = Field(
        None,
        json_schema_extra={"x-sr-order": 302},
        description="Mask video (white areas will be inpainted). Leave blank for video-to-video transformation.",
    )
    
    strength: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        json_schema_extra={"x-sr-order": 303},
        description="Strength of inpainting effect, 1.0 is full regeneration.",
    )
    
    
    inpaint_fixup_steps: int = Field(
        default=0,
        ge=0,
        le=10,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 304},
        description="Number of steps for final inpaint fixup. Ignored when in video-to-video mode (when mask_video is empty).",
    )
    
    expand_mask: int = Field(
        default=10,
        ge=0,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 305},
        description="Expand the mask by a number of pixels.",
    )
    
    keep_aspect_ratio: bool = Field(
        default=False,
        json_schema_extra={"x-sr-order": 401},
        description="Keep the aspect ratio of the input video. This will degrade the quality of the inpainting.",
    )
    
    frames_per_second: int = Field(
        default=16,
        ge=5,
        le=30,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 402},
        description="Output video FPS.",
    )



class Wan2113BInpaintOutput(VideoOutput):
    predict_time: float = Field(
        ...,
        description="Time taken to generate the video",
    )
