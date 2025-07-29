from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class Status(Enum):
    STARTING = "starting"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class Type(Enum):
    PREDICTION = "prediction"


class ReplicateInput(BaseModel):
    """
    Input schema for the TripoSR image to 3D model conversion.

    This class defines the expected input parameters for converting a 2D image
    into a 3D model using TripoSR.
    """
    image_path: str = Field(
        ...,
        title="Image Path",
        description="Input Image",
        json_schema_extra={"x-order": 0}
    )
    do_remove_background: Optional[bool] = Field(
        True,
        title="Do Remove Background",
        json_schema_extra={"x-order": 1}
    )
    foreground_ratio: Optional[float] = Field(
        0.85,
        ge=0.5,
        le=1,
        title="Foreground Ratio",
        json_schema_extra={"x-order": 2}
    )



class ReplicateResponse(BaseModel):
    id: str = Field(..., title="ID")
    version: Optional[str] = Field(None, title="Version")
    created_at: Optional[str] = Field(None, title="Created At")
    started_at: Optional[str] = Field(None, title="Started At")
    completed_at: Optional[str] = Field(None, title="Completed At")
    source: Optional[str] = Field(None, title="Source")
    status: Optional[Status] = Field(None, title="Status")
    input: Optional[ReplicateInput] = Field(None, title="Input")
    output: Optional[List[str]] = Field(None, title="Output")
    error: Optional[str] = Field(None, title="Error")
    logs: Optional[str] = Field(None, title="Logs")
    metrics: Optional[Dict[str, Any]] = Field(None, title="Metrics")
    webhook_completed: Optional[str] = Field(None, title="Webhook Completed")
    type: Optional[Type] = Field(None, title="Type")


class PredictionRequest(BaseModel):
    input: ReplicateInput = Field(..., title="Input")
    webhook: Optional[str] = Field(
        None, title="Webhook", description="Webhook URL for completions."
    )
    webhook_events_filter: Optional[List[str]] = Field(
        None,
        title="Webhook Events Filter",
        description="Events to send to the webhook",
    )


class ValidationError(BaseModel):
    loc: List[str] = Field(..., title="Location")
    msg: str = Field(..., title="Message")
    type: str = Field(..., title="Error Type")


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = Field(None, title="Detail")