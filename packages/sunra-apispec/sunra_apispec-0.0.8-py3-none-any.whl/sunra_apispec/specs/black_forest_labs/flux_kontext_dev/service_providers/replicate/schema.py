from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, RootModel, Field
from datetime import datetime

class AspectRatio(str, Enum):
    """An enumeration for aspect ratios."""
    _1_1 = "1:1"
    _16_9 = "16:9"
    _21_9 = "21:9"
    _3_2 = "3:2"
    _2_3 = "2:3"
    _4_5 = "4:5"
    _5_4 = "5:4"
    _3_4 = "3:4"
    _4_3 = "4:3"
    _9_16 = "9:16"
    _9_21 = "9:21"
    MATCH_INPUT_IMAGE = "match_input_image"

class OutputFormat(str, Enum):
    """An enumeration for output formats."""
    WEBP = "webp"
    JPG = "jpg"
    PNG = "png"

class Status(str, Enum):
    """An enumeration for prediction statuses."""
    STARTING = "starting"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"
    FAILED = "failed"

class WebhookEvent(str, Enum):
    """An enumeration for webhook events."""
    START = "start"
    OUTPUT = "output"
    LOGS = "logs"
    COMPLETED = "completed"

class ReplicateInput(BaseModel):
    """
    Input for the model generation or image editing.
    """
    prompt: str = Field(
        ...,
        json_schema_extra={"x-order": 0},
        description="Text description of what you want to generate, or the instruction on how to edit the given image."
    )
    
    input_image: str = Field(
        ...,
        json_schema_extra={"x-order": 1},
        description="Image to use as reference. Must be jpeg, png, gif, or webp."
    )
    
    aspect_ratio: Optional[AspectRatio] = Field(
        AspectRatio.MATCH_INPUT_IMAGE,
        json_schema_extra={"x-order": 2},
        description="Aspect ratio of the generated image. Use 'match_input_image' to match the aspect ratio of the input image."
    )
    
    num_inference_steps: Optional[int] = Field(
        28,
        ge=4,
        le=50,
        json_schema_extra={"x-order": 3},
        description="Number of inference steps"
    )
    
    guidance: Optional[float] = Field(
        2.5,
        ge=0,
        le=10,
        json_schema_extra={"x-order": 4},
        description="Guidance scale for generation"
    )
    
    seed: Optional[int] = Field(
        None,
        json_schema_extra={"x-order": 5},
        description="Random seed for reproducible generation. Leave blank for random."
    )
    
    output_format: Optional[OutputFormat] = Field(
        "webp",
        json_schema_extra={"x-order": 6},
        description="Output image format"
    )
    
    output_quality: Optional[int] = Field(
        80,
        ge=0,
        le=100,
        json_schema_extra={"x-order": 7},
        description="Quality when saving the output images, from 0 to 100. 100 is best quality, 0 is lowest quality. Not relevant for .png outputs"
    )
    
    disable_safety_checker: Optional[bool] = Field(
        False,
        json_schema_extra={"x-order": 8},
        description="Disable NSFW safety checker"
    )
    
    go_fast: Optional[bool] = Field(
        True,
        json_schema_extra={"x-order": 9},
        description="Make the model go fast, output quality may be slightly degraded for more difficult prompts"
    )

class ReplicateOutput(RootModel[str]):
    """
    Output URI of the generated image.
    """
    pass

class ValidationError(BaseModel):
    """
    Details of a validation error.
    """
    loc: List[Any] = Field(..., title="Location")
    msg: str = Field(..., title="Message")
    type: str = Field(..., title="Error Type")

class HTTPValidationError(BaseModel):
    """
    HTTP validation errors.
    """
    detail: Optional[List[ValidationError]] = Field(None, title="Detail")

class PredictionRequest(BaseModel):
    """
    Request body for a prediction.
    """
    id: Optional[str] = Field(None, title="Id")
    input: Optional[ReplicateInput] = Field(None)
    context: Optional[Dict[str, str]] = Field(None, title="Context", description="Arbitrary user-defined data for the prediction.")
    webhook: Optional[str] = Field(None, min_length=1, max_length=65536, title="Webhook", description="Webhook URL for receiving prediction updates.")
    created_at: Optional[datetime] = Field(None, title="Created At")
    output_file_prefix: Optional[str] = Field(None, title="Output File Prefix")
    webhook_events_filter: Optional[List[WebhookEvent]] = Field(["start", "output", "logs", "completed"], title="Webhook Events Filter")

class PredictionResponse(BaseModel):
    """
    Response body for a prediction.
    """
    id: Optional[str] = Field(None, title="Id")
    logs: str = Field("", title="Logs", description="Logs generated during the prediction.")
    error: Optional[str] = Field(None, title="Error")
    input: Optional[ReplicateInput] = Field(None)
    output: Optional[ReplicateOutput] = None
    status: Optional[Status] = Field(None)
    metrics: Optional[Dict[str, Any]] = Field(None, title="Metrics")
    version: Optional[str] = Field(None, title="Version")
    created_at: Optional[datetime] = Field(None, title="Created At")
    started_at: Optional[datetime] = Field(None, title="Started At")
    completed_at: Optional[datetime] = Field(None, title="Completed At")