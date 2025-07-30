from enum import Enum
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class TargetResolution(str, Enum):
    P720 = "720p"
    P1080 = "1080p"
    K4 = "4k"


class ReplicateInput(BaseModel):
    video: str = Field(..., description="Video file to upscale", json_schema_extra={"x-order": 0})
    target_resolution: Optional[TargetResolution] = Field(
        "1080p", description="Target resolution", json_schema_extra={"x-order": 1}
    )
    target_fps: Optional[int] = Field(
        60, ge=15, le=120, description="Target FPS (choose from 15fps to 120fps)", json_schema_extra={"x-order": 2}
    )


class Output(HttpUrl):
    pass


class Status(str, Enum):
    STARTING = "starting"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"
    FAILED = "failed"


class WebhookEvent(str, Enum):
    START = "start"
    OUTPUT = "output"
    LOGS = "logs"
    COMPLETED = "completed"


class ValidationError(BaseModel):
    loc: List[Union[str, int]] = Field(..., title="Location")
    msg: str = Field(..., title="Message")
    type: str = Field(..., title="Error Type")


class PredictionRequest(BaseModel):
    id: Optional[str] = Field(None, title="Id")
    input: Optional[ReplicateInput] = None
    webhook: Optional[HttpUrl] = Field(
        None,
        min_length=1,
        max_length=65536,
        title="Webhook",
    )
    created_at: Optional[datetime] = Field(None, title="Created At")
    output_file_prefix: Optional[str] = Field(None, title="Output File Prefix")
    webhook_events_filter: Optional[List[WebhookEvent]] = Field(
        ["start", "output", "logs", "completed"], title="Webhook Events Filter"
    )


class PredictionResponse(BaseModel):
    id: Optional[str] = Field(None, title="Id")
    logs: Optional[str] = Field("", title="Logs")
    error: Optional[str] = Field(None, title="Error")
    input: Optional[ReplicateInput] = None
    output: Optional[Output] = None
    status: Optional[Status] = None
    metrics: Optional[Dict[str, Any]] = Field(None, title="Metrics")
    version: Optional[str] = Field(None, title="Version")
    created_at: Optional[datetime] = Field(None, title="Created At")
    started_at: Optional[datetime] = Field(None, title="Started At")
    completed_at: Optional[datetime] = Field(None, title="Completed At")


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = Field(None, title="Detail")