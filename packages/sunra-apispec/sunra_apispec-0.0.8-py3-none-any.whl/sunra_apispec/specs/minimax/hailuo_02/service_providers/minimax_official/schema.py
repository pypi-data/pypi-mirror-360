from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field


class ModelEnum(str, Enum):
    """Available MiniMax models for video generation."""
    MINIMAX_HAILUO_02 = "MiniMax-Hailuo-02"
    T2V_01_DIRECTOR = "T2V-01-Director"
    I2V_01_DIRECTOR = "I2V-01-Director"
    S2V_01 = "S2V-01"
    I2V_01 = "I2V-01"
    I2V_01_LIVE = "I2V-01-live"
    T2V_01 = "T2V-01"


class ResolutionEnum(str, Enum):
    """Available video resolutions."""
    RESOLUTION_720P = "720P"
    RESOLUTION_768P = "768P"
    RESOLUTION_1080P = "1080P"


class DurationEnum(int, Enum):
    """Available video durations in seconds."""
    DURATION_6 = 6
    DURATION_10 = 10


class TaskStatusEnum(str, Enum):
    """Task status values."""
    QUEUEING = "Queueing"
    PREPARING = "Preparing"
    PROCESSING = "Processing"
    SUCCESS = "Success"
    FAIL = "Fail"


class SubjectReference(BaseModel):
    """Subject reference for S2V-01 model."""
    image: str = Field(..., description="Subject reference image URL or base64 encoded data")


class MinimaxVideoGenInput(BaseModel):
    """Input schema for MiniMax video generation API."""
    model: ModelEnum = Field(..., description="ID of model to use for video generation")
    prompt: Optional[str] = Field(
        None, 
        max_length=2000, 
        description="Description of the video. Should be less than 2000 characters."
    )
    prompt_optimizer: Optional[bool] = Field(
        True, 
        description="Whether the model will automatically optimize the incoming prompt to improve generation quality"
    )
    duration: Optional[DurationEnum] = Field(
        None, 
        description="Video length in seconds. Available options vary by model and resolution."
    )
    resolution: Optional[ResolutionEnum] = Field(
        None, 
        description="Video resolution. Available options vary by model and duration."
    )
    first_frame_image: Optional[str] = Field(
        None, 
        description="Image to use as the first frame for image-to-video generation. Can be URL or base64 encoded."
    )
    subject_reference: Optional[List[SubjectReference]] = Field(
        None, 
        max_length=1, 
        description="Subject reference for S2V-01 model. Currently supports only single subject reference."
    )
    callback_url: Optional[str] = Field(
        None, 
        description="URL to receive real-time status update messages."
    )


class BaseResponse(BaseModel):
    """Base response structure for MiniMax API."""
    status_code: int = Field(..., description="Status code of the response")
    status_msg: str = Field(..., description="Status message describing the result")


class MinimaxVideoGenOutput(BaseModel):
    """Output schema for MiniMax video generation API."""
    task_id: str = Field(..., description="The task ID for the asynchronous video generation task")
    base_resp: BaseResponse = Field(..., description="Status code and its details")


class TaskStatusResponse(BaseModel):
    """Response schema for task status query."""
    task_id: str = Field(..., description="The task ID being queried")
    status: TaskStatusEnum = Field(..., description="Current task status")
    file_id: Optional[str] = Field(None, description="File ID of the generated video (available when status is Success)")
    base_resp: BaseResponse = Field(..., description="Status code and its details")


class FileInfo(BaseModel):
    """File information structure."""
    file_id: int = Field(..., description="Unique identifier for the file")
    bytes: int = Field(..., description="File size in bytes")
    created_at: int = Field(..., description="Unix timestamp when the file was created, in seconds")
    filename: str = Field(..., description="The name of the file")
    purpose: str = Field(..., description="The purpose of using the file")
    download_url: str = Field(..., description="The URL to download the video")


class FileRetrieveResponse(BaseModel):
    """Response schema for file retrieval."""
    file: FileInfo = Field(..., description="File information")
    base_resp: BaseResponse = Field(..., description="Status code and its details")


class CallbackValidation(BaseModel):
    """Callback validation request structure."""
    challenge: str = Field(..., description="Challenge value that must be returned for validation")


class CallbackResponse(BaseModel):
    """Callback validation response structure."""
    challenge: str = Field(..., description="Challenge value returned for validation") 