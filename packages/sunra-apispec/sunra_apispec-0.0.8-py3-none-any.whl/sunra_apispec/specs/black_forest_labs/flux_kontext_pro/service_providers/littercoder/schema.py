"""
Schema definitions for Black Forest Labs Official FLUX Kontext Pro API.
Based on the OpenAPI specification from BFL.
"""

from enum import Enum
from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional, Union, Literal


class OutputFormat(str, Enum):
    """Output format enumeration."""
    JPEG = "jpeg"
    PNG = "png"


class LittercoderFluxKontextProInput(BaseModel):
    """Input schema for FLUX Kontext Pro API requests."""
    
    prompt: str = Field(
        ...,
        description="Text prompt for image generation.",
        example="ein fantastisches bild"
    )
    
    input_image: Optional[str] = Field(
        None,
        description="Base64 encoded image to use with Bagel."
    )
    
    seed: Optional[int] = Field(
        None,
        description="Optional seed for reproducibility.",
        example=42
    )
    
    aspect_ratio: Optional[str] = Field(
        None,
        description="Aspect ratio of the image between 21:9 and 9:21"
    )
    
    output_format: Optional[OutputFormat] = Field(
        OutputFormat.PNG,
        description="Output format for the generated image. Can be 'jpeg' or 'png'."
    )
    
    webhook_url: Optional[str] = Field(
        None,
        description="URL to receive webhook notifications",
        max_length=2083,
        min_length=1
    )
    
    webhook_secret: Optional[str] = Field(
        None,
        description="Optional secret for webhook signature verification"
    )
    
    prompt_upsampling: bool = Field(
        False,
        description="Whether to perform upsampling on the prompt. If active, automatically modifies the prompt for more creative generation."
    )
    
    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=6,
        description="Tolerance level for input and output moderation. Between 0 and 6, 0 being most strict, 6 being least strict.",
    )


class LittercoderAsyncResponse(BaseModel):
    """Response schema for async task submission."""
    
    id: str = Field(
        ...,
        description="Task ID for retrieving result"
    )
    
    polling_url: str = Field(
        ...,
        description="URL for polling task status"
    )


class LittercoderResultResponse(BaseModel):
    """Response schema for task results."""
    
    id: str = Field(
        ...,
        description="Task id for retrieving result"
    )
    
    status: str = Field(
        ...,
        description="Task status"
    )
    
    result: Optional[dict] = Field(
        None,
        description="Task result data"
    )
    
    progress: Optional[float] = Field(
        None,
        description="Task progress percentage"
    )
    
    details: Optional[dict] = Field(
        None,
        description="Additional task details"
    ) 