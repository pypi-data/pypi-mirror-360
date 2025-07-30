from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class ReplicateImagen3FastInput(BaseModel):
    """Input schema for Replicate Imagen3 Fast model."""
    prompt: str = Field(..., description="Text prompt for image generation")
    aspect_ratio: Literal['1:1', '9:16', '16:9', '3:4', '4:3'] = Field(
        '1:1', 
        description="Aspect ratio of the generated image"
    )
    safety_filter_level: Literal[
        'block_low_and_above', 
        'block_medium_and_above', 
        'block_only_high'
    ] = Field(
        'block_medium_and_above',
        description="block_low_and_above is strictest, block_medium_and_above blocks some prompts, block_only_high is most permissive but some prompts will still be blocked"
    )


class ReplicateImagen3FastOutput(BaseModel):
    """Output schema for Replicate Imagen3 Fast model."""
    url: str = Field(..., description="URL of the generated image")


class ReplicateImagen3FastStatus(BaseModel):
    """Status enumeration for prediction."""
    status: Literal["starting", "processing", "succeeded", "canceled", "failed"]


class ReplicateImagen3FastPredictionRequest(BaseModel):
    """Request schema for creating a prediction."""
    input: ReplicateImagen3FastInput
    webhook: Optional[str] = Field(None, description="Webhook URL for notifications")


class ReplicateImagen3FastPredictionResponse(BaseModel):
    """Response schema for prediction."""
    id: str
    input: ReplicateImagen3FastInput
    output: Optional[str] = None
    status: Literal["starting", "processing", "succeeded", "canceled", "failed"]
    error: Optional[str] = None
    logs: str = ""
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None 