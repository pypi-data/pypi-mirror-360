from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class ReplicateVeo2Input(BaseModel):
    """Input schema for Replicate Veo2 model."""
    prompt: Optional[str] = Field(None, description="Text prompt for video generation")
    image: Optional[str] = Field(
        None, 
        description="Input image to start generating from. Ideal images are 16:9 or 9:16 and 1280x720 or 720x1280, depending on the aspect ratio you choose."
    )
    aspect_ratio: Literal['16:9', '9:16'] = Field(
        '16:9', 
        description="Video aspect ratio"
    )
    duration: Literal[5, 6, 7, 8] = Field(
        5,
        description="Video duration"
    )
    seed: Optional[int] = Field(None, description="Random seed. Omit for random generations")


class ReplicateVeo2Output(BaseModel):
    """Output schema for Replicate Veo2 model."""
    url: str = Field(..., description="URL of the generated video")


class ReplicateVeo2Status(BaseModel):
    """Status enumeration for prediction."""
    status: Literal["starting", "processing", "succeeded", "canceled", "failed"]


class ReplicateVeo2PredictionRequest(BaseModel):
    """Request schema for creating a prediction."""
    input: ReplicateVeo2Input
    webhook: Optional[str] = Field(None, description="Webhook URL for notifications")


class ReplicateVeo2PredictionResponse(BaseModel):
    """Response schema for prediction."""
    id: str
    input: ReplicateVeo2Input
    output: Optional[str] = None
    status: Literal["starting", "processing", "succeeded", "canceled", "failed"]
    error: Optional[str] = None
    logs: str = ""
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None 
