from enum import Enum
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class EnhanceModel(str, Enum):
    STANDARD_V2 = "Standard V2"
    LOW_RESOLUTION_V2 = "Low Resolution V2"
    CGI = "CGI"
    HIGH_FIDELITY_V2 = "High Fidelity V2"
    TEXT_REFINE = "Text Refine"


class OutputFormat(str, Enum):
    JPG = "jpg"
    PNG = "png"


class UpscaleFactor(str, Enum):
    NONE = "None"
    X2 = "2x"
    X4 = "4x"
    X6 = "6x"


class SubjectDetection(str, Enum):
    NONE = "None"
    ALL = "All"
    FOREGROUND = "Foreground"
    BACKGROUND = "Background"


class ReplicateInput(BaseModel):
    image: str = Field(..., description="Image to enhance", json_schema_extra={"x-order": 0})
    enhance_model: Optional[EnhanceModel] = Field(
        EnhanceModel.STANDARD_V2,
        description="Model to use: Standard V2 (general purpose), Low Resolution V2 (for low-res images), CGI (for digital art), High Fidelity V2 (preserves details), Text Refine (optimized for text)",
        json_schema_extra={"x-order": 1},
    )
    output_format: Optional[OutputFormat] = Field(
        OutputFormat.JPG, description="Output format", json_schema_extra={"x-order": 3}
    )
    upscale_factor: Optional[UpscaleFactor] = Field(
        UpscaleFactor.NONE, description="How much to upscale the image", json_schema_extra={"x-order": 2}
    )
    face_enhancement: Optional[bool] = Field(
        False, description="Enhance faces in the image", json_schema_extra={"x-order": 5}
    )
    subject_detection: Optional[SubjectDetection] = Field(
        SubjectDetection.NONE, description="Subject detection", json_schema_extra={"x-order": 4}
    )
    face_enhancement_strength: Optional[float] = Field(
        0.8,
        ge=0,
        le=1,
        description="Control how sharp the enhanced faces are relative to the background from 0 to 1. Defaults to 0.8, and is ignored if face_enhancement is false.",
        json_schema_extra={"x-order": 7},
    )
    face_enhancement_creativity: Optional[float] = Field(
        0,
        ge=0,
        le=1,
        description="Choose the level of creativity for face enhancement from 0 to 1. Defaults to 0, and is ignored if face_enhancement is false.",
        json_schema_extra={"x-order": 6},
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