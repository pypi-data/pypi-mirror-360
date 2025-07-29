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


class BFLFluxV1ProUltraInput(BaseModel):
    """Input schema for FLUX 1.1 Pro Ultra image generation."""
    
    prompt: Optional[str] = Field(
        default="",
        description="The prompt to use for image generation.",
        examples=["A beautiful landscape with mountains and a lake"]
    )
    
    prompt_upsampling: bool = Field(
        default=False,
        description="Whether to perform upsampling on the prompt. If active, automatically modifies the prompt for more creative generation."
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Optional seed for reproducibility. If not provided, a random seed will be used.",
        examples=[42]
    )
    
    aspect_ratio: str = Field(
        default="16:9",
        description="Aspect ratio of the image between 21:9 and 9:21"
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
    
    raw: bool = Field(
        default=False,
        description="Generate less processed, more natural-looking images",
        examples=[False]
    )
    
    image_prompt: Optional[str] = Field(
        default=None,
        description="Optional image to remix in base64 format"
    )
    
    image_prompt_strength: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Blend between the prompt and the image prompt"
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
BFLFluxV1ProUltraOutput = Union[AsyncResponse, AsyncWebhookResponse] 
