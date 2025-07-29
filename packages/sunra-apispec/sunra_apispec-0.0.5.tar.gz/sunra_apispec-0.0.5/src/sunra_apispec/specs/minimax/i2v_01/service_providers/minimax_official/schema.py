# Schema for MiniMax Video Generation
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class ModelEnum(str, Enum):
    T2V_01 = "T2V-01"
    T2V_01_DIRECTOR = "T2V-01-Director"
    I2V_01 = "I2V-01"
    I2V_01_DIRECTOR = "I2V-01-Director"
    I2V_01_LIVE = "I2V-01-live"
    S2V_01 = "S2V-01"


class SubjectReferenceItem(BaseModel):
    """Subject reference for S2V-01 model"""
    type: Literal["character"] = Field(..., description="Subject type, currently only\"character\"is supported, which refers to a human face as the subject.")

    image: List[str] = Field(..., description="This field accepts either a Base64-encoded string in the data:image/jpeg;base64, format or a publicly accessible URL, stored as a string in an array (the array length currently supports only 1, i.e., a single reference image). The reference image must be under 20MB in size, and supported formats include JPG, JPEG, and PNG. Note: The image must contain valid subject information; otherwise, the video generation process will fail (task creation will not be blocked). In such cases, the query API will return a failure status for the video generation task.")

class MinimaxVideoGenInput(BaseModel):
    """Input schema for MiniMax Video Generation API"""
    
    model: ModelEnum = Field(
        ...,
        description="ID of the model to use for video generation"
    )
    
    prompt: Optional[str] = Field(None,
        max_length=2000,
        description=(
            "Description of the video. Should be less than 2000 characters. "
            "For Director models, supports camera movement instructions in [] format. "
            "Supported movements: [Truck left/right], [Pan left/right], [Push in/Pull out], "
            "[Pedestal up/down], [Tilt up/down], [Zoom in/out], [Shake], [Tracking shot], [Static shot]"
        )
    )
    
    prompt_optimizer: bool = Field(True,
        description=(
            "Whether to use the model's prompt optimizer to improve generation quality. "
            "Set to False for more precise control over the prompt"
        )
    )
    
    first_frame_image: Optional[str] = Field(None,
        description=(
            "The image to use as the first frame for video generation. "
            "Required for I2V-01, I2V-01-Director, and I2V-01-live models. "
            "Supports URL or base64 encoding. "
            "Format: JPG, JPEG, or PNG. Aspect ratio: 2:5 to 5:2. "
            "Shorter side > 300px. Max size: 20MB"
        )
    )
    
    subject_reference: Optional[List[SubjectReferenceItem]] = Field(None,
        max_items=1,
        description=(
            "Subject reference for S2V-01 model only. "
            "Currently supports only a single subject reference (array length is 1)"
        )
    )
    
    callback_url: Optional[str] = Field(None,
        description=(
            "Optional callback URL to receive real-time status updates. "
            "Must respond to validation challenge within 3 seconds"
        )
    )
