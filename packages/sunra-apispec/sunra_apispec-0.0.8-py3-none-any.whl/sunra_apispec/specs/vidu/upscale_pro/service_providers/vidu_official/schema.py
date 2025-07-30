"""
Schema for Vidu Official Upscale Pro API service provider.
Based on Vidu platform API documentation from:
- https://platform.vidu.com/upscale-pro
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
from enum import Enum


class UpscaleResolutionEnum(str, Enum):
    """Available upscale resolution options."""
    R1080P = "1080p"
    R2K = "2K"
    R4K = "4K"
    R8K = "8K"


class TaskStateEnum(str, Enum):
    """Task processing states."""
    CREATED = "created"
    QUEUEING = "queueing"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class UpscaleProInput(BaseModel):
    """Schema for video upscaling using Vidu Upscale Pro API."""
    
    video_url: Optional[str] = Field(
        None,
        description="The URL of the video to be upscaled. "
                   "Requirements: "
                   "- URL must be accessible. "
                   "- Supported container formats: MP4, FLV, HLS, MXF, MOV, TS, WEBM, MKV. "
                   "- Supported video codecs: H.264, H.264 intra, H.265, AV1, H.266, MV-HEVC, MPEG2, VP8, VP9. "
                   "- Maximum video duration: 300 seconds. "
                   "- Frame rate must be below 60 FPS."
    )
    
    video_creation_id: Optional[str] = Field(
        None,
        description="Unique ID of the video generation task on Vidu. "
                   "Must be retrieved from creation_id using the GetGeneration API, "
                   "request URL {/ent/v2/tasks/{id}/creations}. "
                   "Note: If both video_creation_id and video_url are provided, "
                   "the system will prioritize video_creation_id and ignore video_url."
    )
    
    upscale_resolution: Optional[UpscaleResolutionEnum] = Field(
        UpscaleResolutionEnum.R1080P,
        description="Target resolution for upscaling. "
                   "Default is 1080p. Accept values: 1080p, 2K, 4K, 8K. "
                   "The resolution must be higher than the original video resolution, "
                   "otherwise the task will fail."
    )
    
    callback_url: Optional[str] = Field(
        None,
        description="Callback URL. When creating a task, you can set the callback_url "
                   "with a POST request. When the video upscaling task changes its status, "
                   "Vidu will send a callback request to this URL, containing the latest "
                   "status of the task. The status includes: processing, success, failed."
    )
    

class UpscaleProResponse(BaseModel):
    """Response schema for video upscaling."""
    
    task_id: str = Field(
        ...,
        description="Task ID for tracking the upscaling process"
    )
    
    state: TaskStateEnum = Field(
        ...,
        description="Processing state: created, queueing, processing, success, failed"
    )
    
    video_url: Optional[str] = Field(
        None,
        description="The video URL submitted for upscaling"
    )
    
    video_creation_id: Optional[str] = Field(
        None,
        description="The video creation id submitted for upscaling"
    )
    
    upscale_resolution: str = Field(
        ...,
        description="The resolution used for upscaling"
    )
    
    created_at: str = Field(
        ...,
        description="Task creation time in ISO format"
    )
