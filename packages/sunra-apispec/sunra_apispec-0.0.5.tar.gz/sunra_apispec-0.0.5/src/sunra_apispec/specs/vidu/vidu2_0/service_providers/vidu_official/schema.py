"""
Schema for Vidu Official API service provider.
Based on Vidu platform API documentation from:
- https://platform.vidu.com/text-to-video
- https://platform.vidu.com/image-to-video  
- https://platform.vidu.com/reference-to-video
- https://platform.vidu.com/start-end-to-video
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ModelEnum(str, Enum):
    """Available models for Vidu video generation."""
    VIDUQ1 = "viduq1"
    VIDU1_5 = "vidu1.5"
    VIDU2_0 = "vidu2.0"


class TaskStateEnum(str, Enum):
    """Task processing states."""
    CREATED = "created"
    QUEUEING = "queueing"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class ViduTextToVideoInput(BaseModel):
    """Schema for text-to-video generation using Vidu API."""
    
    model: ModelEnum = Field(
        ...,
        description="Model name. Accepted values: viduq1, vidu1.5"
    )
    
    style: Optional[str] = Field(
        "general",
        description="The style of output video. Defaults to general. "
                   "general: General style, allows style control through prompts. "
                   "anime: Anime style, optimized for anime aesthetics."
    )
    
    prompt: str = Field(
        ...,
        max_length=1500,
        description="Text prompt. A textual description for video generation, "
                   "with a maximum length of 1500 characters."
    )
    
    duration: Optional[int] = Field(
        None,
        description="Video duration in seconds. Default values vary by model: "
                   "viduq1: default 5s, available: 5. "
                   "vidu1.5: default 4s, available: 4, 8."
    )
    
    seed: Optional[int] = Field(
        None,
        description="Random seed. Defaults to a random seed number. "
                   "Manually set values will override the default random seed."
    )
    
    aspect_ratio: Optional[str] = Field(
        "16:9",
        description="The aspect ratio of the output video. "
                   "Defaults to 16:9, accepted: 16:9, 9:16, 1:1."
    )
    
    resolution: Optional[str] = Field(
        "360p",
        description="Resolution. Default values vary by model & duration: "
                   "viduq1 (5s): default 1080p, available: 1080p. "
                   "vidu1.5 (4s): default 360p, available: 360p, 720p, 1080p. "
                   "vidu1.5 (8s): default 720p, available: 720p."
    )
    
    movement_amplitude: Optional[str] = Field(
        "auto",
        description="The movement amplitude of objects in the frame. "
                   "Defaults to auto, accepted values: auto, small, medium, large."
    )
    
    callback_url: Optional[str] = Field(
        None,
        description="Callback URL. When creating a task, you can set the callback_url "
                   "with a POST request. When the video generation task changes its status, "
                   "Vidu will send a callback request to this URL."
    )


class ViduImageToVideoInput(BaseModel):
    """Schema for image-to-video generation using Vidu API."""
    
    model: ModelEnum = Field(
        ...,
        description="Model name. Accepted values: viduq1, vidu2.0, vidu1.5"
    )
    
    images: List[str] = Field(
        ...,
        min_items=1,
        max_items=1,
        description="An image to be used as the start frame of the generated video. "
                   "Only accepts 1 image. Accepts public URL or Base64 format. "
                   "Supported formats: png, jpeg, jpg, webp. "
                   "The aspect ratio of the images must be less than 1:4 or 4:1. "
                   "All images are limited to 50MB."
    )
    
    prompt: Optional[str] = Field(
        None,
        max_length=1500,
        description="Text prompt. A textual description for video generation, "
                   "with a maximum length of 1500 characters."
    )
    
    duration: Optional[int] = Field(
        4,
        description="Video duration in seconds. Default values vary by model: "
                   "viduq1: default 5s, available: 5. "
                   "vidu2.0 and vidu1.5: default 4s, available: 4, 8."
    )
    
    seed: Optional[int] = Field(
        None,
        description="Random seed. Defaults to a random seed number. "
                   "Manually set values will override the default random seed."
    )
    
    resolution: Optional[str] = Field(
        "360p",
        description="Resolution based on model & duration: "
                   "viduq1 (5s): default 1080p, options: 1080p. "
                   "vidu2.0 and vidu1.5 (4s): default 360p, options: 360p, 720p, 1080p. "
                   "vidu2.0 and vidu1.5 (8s): default 720p, options: 720p."
    )
    
    movement_amplitude: Optional[str] = Field(
        "auto",
        description="The movement amplitude of objects in the frame. "
                   "Defaults to auto, accepted values: auto, small, medium, large."
    )
    
    callback_url: Optional[str] = Field(
        None,
        description="Callback URL. When creating a task, you can set the callback_url "
                   "with a POST request. When the video generation task changes its status, "
                   "Vidu will send a callback request to this URL."
    )


class ViduReferenceImagesToVideoInput(BaseModel):
    """Schema for reference-to-video generation using Vidu API."""
    
    model: ModelEnum = Field(
        ...,
        description="Model name. Accepted values: vidu2.0, vidu1.5"
    )
    
    images: List[str] = Field(
        ...,
        min_items=1,
        max_items=3,
        description="The model will use the provided images as references to generate "
                   "a video with consistent subjects. Accepts 1 to 3 images. "
                   "Images Assets can be provided via URLs or Base64 encode. "
                   "Supported formats: PNG, JPEG, JPG, WebP. "
                   "The dimensions of the images must be at least 128x128 pixels. "
                   "The aspect ratio of the images must be less than 1:4 or 4:1. "
                   "All images are limited to 50MB."
    )
    
    prompt: str = Field(
        ...,
        max_length=1500,
        description="Text prompt. A textual description for video generation, "
                   "with a maximum length of 1500 characters."
    )
    
    duration: Optional[int] = Field(
        4,
        description="The number of seconds of duration for the output video. "
                   "Default to 4, accepted values: 4, 8. "
                   "But vidu2.0 only accepts 4."
    )
    
    seed: Optional[int] = Field(
        None,
        description="Random seed. Defaults to a random seed number. "
                   "Manually set values will override the default random seed."
    )
    
    aspect_ratio: Optional[str] = Field(
        "16:9",
        description="The aspect ratio of the output video. "
                   "Defaults to 16:9, accepted: 16:9, 9:16, 1:1."
    )
    
    resolution: Optional[str] = Field(
        "360p",
        description="The resolution of the output video. "
                   "Defaults to 360p, accepted values: 360p, 720p, 1080p. "
                   "Model vidu1.5 duration 4 accepted: 360p, 720p, 1080p. "
                   "Model vidu1.5 duration 8 accepted: 720p. "
                   "Model vidu2.0 duration 4 accepted: 360p, 720p."
    )
    
    movement_amplitude: Optional[str] = Field(
        "auto",
        description="The movement amplitude of objects in the frame. "
                   "Defaults to auto, accepted values: auto, small, medium, large."
    )
    
    callback_url: Optional[str] = Field(
        None,
        description="Callback URL. When creating a task, you can set the callback_url "
                   "with a POST request. When the video generation task changes its status, "
                   "Vidu will send a callback request to this URL."
    )


class ViduStartEndToVideoInput(BaseModel):
    """Schema for start-end-to-video generation using Vidu API."""
    
    model: ModelEnum = Field(
        ...,
        description="Model name. Accepted values: viduq1, vidu2.0, vidu1.5"
    )
    
    images: List[str] = Field(
        ...,
        min_items=2,
        max_items=2,
        description="Two images: first is start frame, second is end frame. "
                   "Notes: "
                   "1. Public URL or Base64 format supported. "
                   "2. Aspect ratios must be close: ratio between start/end frame must be in 0.8~1.25. "
                   "3. Supported formats: png, jpeg, jpg, webp. "
                   "4. Maximum size: 50MB per image. "
                   "5. Base64 format must include content type string, e.g., image/png;base64,{base64_encode}."
    )
    
    prompt: Optional[str] = Field(
        None,
        max_length=1500,
        description="Prompt description, maximum 1500 characters."
    )
    
    duration: Optional[int] = Field(
        4,
        description="Video duration in seconds. Default values vary by model: "
                   "viduq1: default 5s, available: 5. "
                   "vidu2.0 and vidu1.5: default 4s, available: 4, 8."
    )
    
    seed: Optional[int] = Field(
        None,
        description="Random seed. Defaults to a random seed number. "
                   "Manually set values will override the default random seed."
    )
    
    resolution: Optional[str] = Field(
        "360p",
        description="Resolution based on model & duration: "
                   "viduq1 (5s): default 1080p, options: 1080p. "
                   "vidu2.0 and vidu1.5 (4s): default 360p, options: 360p, 720p, 1080p. "
                   "vidu2.0 and vidu1.5 (8s): default 720p, options: 720p."
    )
    
    movement_amplitude: Optional[str] = Field(
        "auto",
        description="The movement amplitude of objects in the frame. "
                   "Defaults to auto, accepted values: auto, small, medium, large."
    )
    
    callback_url: Optional[str] = Field(
        None,
        description="Callback URL. When creating a task, you can set the callback_url "
                   "with a POST request. When the video generation task changes its status, "
                   "Vidu will send a callback request to this URL."
    )


class ViduVideoGenerationResponse(BaseModel):
    """Response schema for all video generation endpoints."""
    
    task_id: str = Field(
        ...,
        description="Task ID for tracking the generation process"
    )
    
    state: TaskStateEnum = Field(
        ...,
        description="Processing state: created, queueing, processing, success, failed"
    )
    
    model: str = Field(
        ...,
        description="The parameter of the model used for this call"
    )
    
    prompt: Optional[str] = Field(
        None,
        description="The text prompt used for this call"
    )
    
    images: Optional[List[str]] = Field(
        None,
        description="The images used for this call (for image/reference-to-video)"
    )
    
    style: Optional[str] = Field(
        None,
        description="The style parameter used for this call (for text-to-video)"
    )
    
    duration: Optional[int] = Field(
        None,
        description="The video duration parameter used for this call"
    )
    
    seed: Optional[int] = Field(
        None,
        description="The random seed parameter used for this call"
    )
    
    aspect_ratio: Optional[str] = Field(
        None,
        description="The aspect ratio parameter used for this call"
    )
    
    resolution: Optional[str] = Field(
        None,
        description="The resolution parameter used for this call"
    )
    
    movement_amplitude: Optional[str] = Field(
        None,
        description="The camera movement amplitude parameter used for this call"
    )
    
    created_at: str = Field(
        ...,
        description="Task creation time in ISO format"
    )
