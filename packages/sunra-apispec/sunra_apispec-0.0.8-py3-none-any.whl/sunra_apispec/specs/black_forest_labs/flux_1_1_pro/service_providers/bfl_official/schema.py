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


class BFLFluxV11ProInput(BaseModel):
    """Input schema for FLUX 1.1 Pro image generation."""
    
    prompt: Optional[str] = Field(
        default="",
        description="Text prompt for image generation.",
        examples=["ein fantastisches bild"]
    )
    
    image_prompt: Optional[str] = Field(
        default=None,
        description="Optional base64 encoded image to use with Flux Redux."
    )
    
    width: int = Field(
        default=1024,
        ge=256,
        le=1440,
        multiple_of=32,
        description="Width of the generated image in pixels. Must be a multiple of 32."
    )
    
    height: int = Field(
        default=768,
        ge=256,
        le=1440,
        multiple_of=32,
        description="Height of the generated image in pixels. Must be a multiple of 32."
    )
    
    prompt_upsampling: bool = Field(
        default=False,
        description="Whether to perform upsampling on the prompt. If active, automatically modifies the prompt for more creative generation."
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Optional seed for reproducibility.",
        examples=[42]
    )
    
    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=6,
        description="Tolerance level for input and output moderation. Between 0 and 6, 0 being most strict, 6 being least strict.",
        examples=[2]
    )
    
    output_format: Optional[OutputFormat] = Field(
        default=OutputFormat.JPEG,
        description="Output format for the generated image. Can be 'jpeg' or 'png'."
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


class AsyncResponse(BaseModel):
    """Response for async task submission."""
    
    id: str = Field(description="Task ID for retrieving result")
    polling_url: str = Field(description="URL for polling task status")


class AsyncWebhookResponse(BaseModel):
    """Response for async task submission with webhook."""
    
    id: str = Field(description="Task ID for retrieving result")
    status: str = Field(description="Current task status")
    webhook_url: str = Field(description="Webhook URL for notifications")


class ResultResponse(BaseModel):
    """Response containing task result."""
    
    id: str = Field(description="Task id for retrieving result")
    status: StatusResponse = Field(description="Current task status")
    result: Optional[dict] = Field(default=None, description="Task result data")
    progress: Optional[float] = Field(default=None, description="Task progress (0-1)")
    details: Optional[dict] = Field(default=None, description="Additional task details")


# Union type for generation response
BFLFluxV11ProOutput = Union[AsyncResponse, AsyncWebhookResponse]
