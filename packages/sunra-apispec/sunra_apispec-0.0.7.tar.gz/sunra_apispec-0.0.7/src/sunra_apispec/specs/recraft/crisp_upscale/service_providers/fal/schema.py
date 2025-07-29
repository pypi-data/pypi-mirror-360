from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class QueueStatusStatus(str, Enum):
    IN_QUEUE = "IN_QUEUE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class File(BaseModel):
    """
    File
    """

    url: str = Field(..., description="The URL where the file can be downloaded from.", json_schema_extra={"x-order": 0})
    content_type: Optional[str] = Field(None, description="The mime type of the file.", json_schema_extra={"x-order": 1})
    file_name: Optional[str] = Field(None, description="The name of the file. It will be auto-generated if not provided.", json_schema_extra={"x-order": 2})
    file_size: Optional[int] = Field(None, description="The size of the file in bytes.", json_schema_extra={"x-order": 3})
    file_data: Optional[str] = Field(None, description="File data", json_schema_extra={"x-order": 4})


class QueueStatus(BaseModel):
    """
    QueueStatus
    """

    status: QueueStatusStatus = Field(..., description="status")
    request_id: str = Field(..., description="The request id.")
    response_url: Optional[str] = Field(None, description="The response url.")
    status_url: Optional[str] = Field(None, description="The status url.")
    cancel_url: Optional[str] = Field(None, description="The cancel url.")
    logs: Optional[Dict[str, Any]] = Field(None, description="The logs.")
    metrics: Optional[Dict[str, Any]] = Field(None, description="The metrics.")
    queue_position: Optional[int] = Field(None, description="The queue position.")


class RecraftUpscaleCrispInput(BaseModel):
    """
    UpscaleInput
    """

    image_url: str = Field(..., min_length=1, max_length=2083, description="The URL of the image to be upscaled. Must be in PNG format.", json_schema_extra={"x-order": 0})
    sync_mode: Optional[bool] = Field(False, description="If set to true, the function will wait for the image to be generated and uploaded before returning the response. This will increase the latency of the function but it allows you to get the image directly in the response without going through the CDN.", json_schema_extra={"x-order": 1})
    enable_safety_checker: Optional[bool] = Field(False, description="If set to true, the safety checker will be enabled.", json_schema_extra={"x-order": 2})


class RecraftUpscaleCrispOutput(BaseModel):
    """
    UpscaleOutput
    """

    image: File = Field(..., description="The upscaled image.", json_schema_extra={"x-order": 0})