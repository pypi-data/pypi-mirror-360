from pydantic import BaseModel, Field
from typing import Optional, Literal


class FalInput(BaseModel):
    """Input model for Wan2.1 FLF2V 14B 720P Fal service provider."""
    
    prompt: str = Field(description="The text prompt to guide video generation.")
    start_image_url: str = Field(description="URL of the starting image. If the input image does not match the chosen aspect ratio, it is resized and center cropped.")
    end_image_url: str = Field(description="URL of the ending image. If the input image does not match the chosen aspect ratio, it is resized and center cropped.")
    
    negative_prompt: Optional[str] = Field(
        default="bright colors, overexposed, static, blurred details, subtitles, style, artwork, painting, picture, still, overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, extra fingers, poorly drawn hands, poorly drawn faces, deformed, disfigured, malformed limbs, fused fingers, still picture, cluttered background, three legs, many people in the background, walking backwards",
        description="Negative prompt for video generation."
    )
    
    num_frames: Optional[int] = Field(
        default=81,
        ge=81,
        le=100,
        description="Number of frames to generate. Must be between 81 to 100 (inclusive)."
    )
    
    frames_per_second: Optional[int] = Field(
        default=16,
        ge=5,
        le=24,
        description="Frames per second of the generated video. Must be between 5 to 24."
    )
    
    resolution: Optional[Literal["480p", "720p"]] = Field(
        default="720p",
        description="Resolution of the generated video (480p or 720p)."
    )
    
    aspect_ratio: Optional[Literal["auto", "16:9", "9:16", "1:1"]] = Field(
        default="auto",
        description="Aspect ratio of the generated video."
    )
    
    num_inference_steps: Optional[int] = Field(
        default=30,
        ge=2,
        le=40,
        description="Number of inference steps for sampling."
    )
    
    guide_scale: Optional[float] = Field(
        default=5.0,
        ge=1.0,
        le=10.0,
        description="Classifier-free guidance scale."
    )
    
    shift: Optional[float] = Field(
        default=5.0,
        ge=1.0,
        le=10.0,
        description="Shift parameter for video generation."
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducibility."
    )
    
    enable_safety_checker: Optional[bool] = Field(
        default=False,
        description="If set to true, the safety checker will be enabled."
    )
    
    enable_prompt_expansion: Optional[bool] = Field(
        default=False,
        description="Whether to enable prompt expansion."
    )
    
    acceleration: Optional[Literal["none", "regular"]] = Field(
        default="regular",
        description="Acceleration level to use."
    )
