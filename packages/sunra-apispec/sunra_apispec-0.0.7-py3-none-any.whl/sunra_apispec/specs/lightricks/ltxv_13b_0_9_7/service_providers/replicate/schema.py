from pydantic import BaseModel, Field


class ReplicateInput(BaseModel):
    """Input schema for Replicate LTX Video API based on openapi.json."""
    
    prompt: str = Field(
        ...,
        description="Text prompt for video generation"
    )
    
    image: str = Field(
        None,
        description="Input image for image-to-video generation. If not provided, text-to-video generation will be used."
    )
    
    negative_prompt: str = Field(
        "worst quality, inconsistent motion, blurry, jittery, distorted",
        description="Negative prompt for video generation."
    )
    
    width: int = Field(
        704,
        description="Width of the output video. Actual width will be a multiple of 32."
    )
    
    height: int = Field(
        480,
        description="Height of the output video. Actual height will be a multiple of 32."
    )
    
    num_frames: int = Field(
        161,
        description="Number of frames to generate. Actual frame count will be 8N+1 (e.g., 9, 17, 25, 161)."
    )
    
    num_inference_steps: int = Field(
        50,
        description="Number of denoising steps."
    )
    
    guidance_scale: float = Field(
        3.0,
        ge=1.0,
        le=10.0,
        multiple_of=0.1,
        description="Guidance scale. Recommended range: 3.0-3.5."
    )
    
    fps: int = Field(
        24,
        description="Frames per second for the output video."
    )
    
    seed: int = Field(
        None,
        description="Random seed for reproducible results. Leave blank for a random seed."
    ) 