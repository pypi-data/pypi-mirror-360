from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List, Union, Literal


class FalInput(BaseModel):
    """Input schema for Pika 1.5 Pikaffects model on FAL."""
    pikaffect: Literal[
        "Melt", "Cake-ify", "Crumble", "Crush", "Decapitate", 
        "Deflate", "Dissolve", "Explode", "Eye-pop", "Inflate", 
        "Levitate", "Peel", "Poke", "Squish", "Ta-da", "Tear"
    ] = Field(
        default="Melt",
        description="The Pikaffect to apply"
    )
    prompt: str = Field(
        ...,
        description="Text prompt to guide the effect"
    )
    image_url: str = Field(
        ...,
        description="URL of the input image"
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        description="Negative prompt to guide the model"
    )
    seed: Optional[int] = Field(
        default=None,
        description="The seed for the random number generator"
    )


class File(BaseModel):
    url: str
    file_size: Optional[int] = None
    file_name: Optional[str] = None
    content_type: Optional[str] = None


class FalOutput(BaseModel):
    """Output schema for Pika 1.5 Pikaffects model on FAL."""
    video: File = Field(
        ...,
        description="The generated video with applied effect"
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
