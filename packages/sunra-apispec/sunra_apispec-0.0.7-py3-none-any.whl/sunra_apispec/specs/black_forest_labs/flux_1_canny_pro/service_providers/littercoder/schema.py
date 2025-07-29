"""
Schema definitions for Littercoder FLUX 1.0 Canny Pro API.
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


class LittercoderFluxV1CannyProInput(BaseModel):
    """Input schema for FLUX Canny Pro image generation."""
    
    prompt: str = Field(
        description="Text prompt for image generation",
        examples=["ein fantastisches bild"]
    )
    
    control_image: Optional[str] = Field(
        default=None,
        description="Base64 encoded image to use as control input if no preprocessed image is provided"
    )
    
    preprocessed_image: Optional[str] = Field(
        default=None,
        description="Optional pre-processed image that will bypass the control preprocessing step"
    )
    
    canny_low_threshold: Optional[int] = Field(
        default=50,
        ge=0,
        le=500,
        description="Low threshold for Canny edge detection"
    )
    
    canny_high_threshold: Optional[int] = Field(
        default=200,
        ge=0,
        le=500,
        description="High threshold for Canny edge detection"
    )
    
    prompt_upsampling: Optional[bool] = Field(
        default=False,
        description="Whether to perform upsampling on the prompt"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Optional seed for reproducibility",
        examples=[42]
    )
    
    steps: Optional[int] = Field(
        default=50,
        ge=15,
        le=50,
        description="Number of steps for the image generation process"
    )
    
    output_format: Optional[OutputFormat] = Field(
        default=OutputFormat.JPEG,
        description="Output format for the generated image. Can be 'jpeg' or 'png'."
    )
    
    guidance: Optional[float] = Field(
        default=30.0,
        ge=1.0,
        le=100.0,
        description="Guidance strength for the image generation process"
    )
    
    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=6,
        description="Tolerance level for input and output moderation. Between 0 and 6, 0 being most strict, 6 being least strict."
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
LittercoderFluxV1CannyProOutput = Union[LittercoderAsyncResponse, LittercoderAsyncWebhookResponse] 
