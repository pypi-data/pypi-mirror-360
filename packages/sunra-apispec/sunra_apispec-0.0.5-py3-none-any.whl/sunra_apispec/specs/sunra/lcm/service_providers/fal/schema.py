from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict


class FalInput(BaseModel):
    """Input schema for LCM model on FAL."""
    prompt: str = Field(
        ...,
        description="The prompt to generate the image from."
    )


class File(BaseModel):
    url: str


class FalOutput(BaseModel):
    images: List[File] = Field(
        ...,
        description="The generated images."
    )


class QueueStatus(BaseModel):
    """Status schema for FAL queue."""
    status: str
    request_id: str
    response_url: Optional[str] = None
    status_url: Optional[str] = None
    cancel_url: Optional[str] = None
    logs: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    queue_position: Optional[int] = None
