"""
Schema definitions for Littercoder FLUX 1.0 Fill Pro API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Union, Literal
from enum import Enum


class OutputFormat(str, Enum):
    """Output format for the generated image."""
    JPEG = "jpeg"
    PNG = "png"


class StatusResponse(str, Enum):
    """Status of the generation task."""
    TASK_NOT_FOUND = "Task not found"
    PENDING = "Pending"
    REQUEST_MODERATED = "Request Moderated"
    CONTENT_MODERATED = "Content Moderated"
    READY = "Ready"
    ERROR = "Error"


class LittercoderFluxV1FillProInput(BaseModel):
    """Input schema for FLUX Fill Pro image generation."""
    
    image: str = Field(
        description="A Base64-encoded string representing the image you wish to modify. Can contain alpha mask if desired."
    )
    
    mask: Optional[str] = Field(
        default=None,
        description="A Base64-encoded string representing a mask for the areas you want to modify in the image. The mask should be the same dimensions as the image and in black and white. Black areas (0%) indicate no modification, while white areas (100%) specify areas for inpainting. Optional if you provide an alpha mask in the original image."
    )
    
    prompt: Optional[str] = Field(
        default="",
        description="The description of the changes you want to make. This text guides the inpainting process, allowing you to specify features, styles, or modifications for the masked area.",
        examples=["ein fantastisches bild"]
    )
    
    steps: Optional[int] = Field(
        default=50,
        ge=15,
        le=50,
        description="Number of steps for the image generation process",
        examples=[50]
    )
    
    prompt_upsampling: Optional[bool] = Field(
        default=False,
        description="Whether to perform upsampling on the prompt. If active, automatically modifies the prompt for more creative generation"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Optional seed for reproducibility"
    )
    
    guidance: Optional[float] = Field(
        default=60.0,
        ge=1.5,
        le=100.0,
        description="Guidance strength for the image generation process"
    )
    
    output_format: Optional[OutputFormat] = Field(
        default=OutputFormat.JPEG,
        description="Output format for the generated image. Can be 'jpeg' or 'png'."
    )
    
    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=6,
        description="Tolerance level for input and output moderation. Between 0 and 6, 0 being most strict, 6 being least strict.",
        examples=[2]
    )
    
    webhook_url: Optional[str] = Field(
        default=None,
        max_length=2083,
        min_length=1,
        description="URL to receive webhook notifications"
    )
    
    webhook_secret: Optional[str] = Field(
        default=None,
        description="Optional secret for webhook signature verification"
    )


class LittercoderAsyncResponse(BaseModel):
    """Response for async task submission."""
    
    id: str = Field(description="Task ID for retrieving result")
    polling_url: str = Field(description="URL for polling task status")


class LittercoderAsyncWebhookResponse(BaseModel):
    """Response for async task submission with webhook."""
    
    id: str = Field(description="Task ID for retrieving result")
    status: str = Field(description="Current task status")
    webhook_url: str = Field(description="Webhook URL for notifications")


class LittercoderResultResponse(BaseModel):
    """Response containing task result."""
    
    id: str = Field(description="Task id for retrieving result")
    status: StatusResponse = Field(description="Current task status")
    result: Optional[dict] = Field(default=None, description="Task result data")
    progress: Optional[float] = Field(default=None, description="Task progress (0-1)")
    details: Optional[dict] = Field(default=None, description="Additional task details")


# Union type for generation response
LittercoderFluxV1FillProOutput = Union[LittercoderAsyncResponse, LittercoderAsyncWebhookResponse] 
