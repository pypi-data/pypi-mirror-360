from pydantic import BaseModel, Field
from typing import Optional, List


class File(BaseModel):
    """File output schema."""
    url: str = Field(description="The URL where the file can be downloaded from.")
    content_type: Optional[str] = Field(default=None, description="The mime type of the file.")
    file_name: Optional[str] = Field(default=None, description="The name of the file.")
    file_size: Optional[int] = Field(default=None, description="The size of the file in bytes.")


class FalUpscaleInput(BaseModel):
    """FAL input schema for image upscaling."""
    
    image_url: str = Field(
        ...,
        description="The image URL to upscale"
    )
    
    prompt: Optional[str] = Field(
        default="",
        description="The prompt to upscale the image with"
    )
    
    detail: int = Field(
        default=50,
        description="The detail of the upscaled image",
        ge=1,
        le=100
    )
    
    resemblance: int = Field(
        default=50,
        description="The resemblance of the upscaled image to the original image",
        ge=1,
        le=100
    )
    
    expand_prompt: bool = Field(
        default=False,
        description="Whether to expand the prompt with MagicPrompt functionality."
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Seed for the random number generator"
    )


class FalUpscaleOutput(BaseModel):
    """FAL output schema for image upscaling."""
    images: List[File] = Field(description="Upscaled images")
    seed: int = Field(description="Seed used for the random number generator") 