from pydantic import BaseModel, Field
from typing import Optional, Literal


class ReplicateInput(BaseModel):
    """Input model for Replicate Photon model."""
    prompt: str = Field(
        ...,
        description="Text prompt for image generation"
    )
    aspect_ratio: Literal["1:1", "3:4", "4:3", "9:16", "16:9", "9:21", "21:9"] = Field(
        "16:9",
        description="Aspect ratio of the generated image"
    )
    image_reference_url: Optional[str] = Field(
        None,
        description="URL of a reference image to guide generation"
    )
    image_reference_weight: Optional[float] = Field(
        0.85,
        description="Weight of the reference image. Larger values will make the reference image have a stronger influence on the generated image."
    )
    style_reference_url: Optional[str] = Field(
        None,
        description="URL of a style reference image"
    )
    style_reference_weight: Optional[float] = Field(
        0.85,
        description="Weight of the style reference image"
    )
    character_reference_url: Optional[str] = Field(
        None,
        description="URL of a character reference image"
    )
    seed: Optional[int] = Field(
        None,
        description="Random seed. Set for reproducible generation"
    )


class ReplicateOutput(BaseModel):
    """Output model for Replicate Photon model."""
    url: str = Field(
        ...,
        description="URL of the generated image"
    ) 