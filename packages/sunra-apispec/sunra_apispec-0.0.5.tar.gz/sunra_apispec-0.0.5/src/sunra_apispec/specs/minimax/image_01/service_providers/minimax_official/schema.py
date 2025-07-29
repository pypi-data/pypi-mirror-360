
# Schema for MiniMax Image Generation
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum

class ModelEnum(str, Enum):
    IMAGE_01 = "image-01"

class SubjectReference(BaseModel):
    """Subject reference for image generation"""
    image_file: str = Field(..., description="URL or base64 encoding of the subject reference image")


class MinimaxImageInput(BaseModel):
    """Input schema for MiniMax Image Generation API"""
    
    model: ModelEnum = Field(
        ModelEnum.IMAGE_01,
        description="MiniMax's high-quality text-to-image & image-to-image model"
    )
    
    prompt: str = Field(...,
        max_length=1500,
        description="Description for the image you want to generate. Should not exceed 1500 characters"
    )
    
    subject_reference: Optional[List[SubjectReference]] = Field(None,
        max_items=1,
        description="Subject reference for image generation. Currently supports only a single subject reference (array length is 1)"
    )
    
    aspect_ratio: Optional[Literal[
        "1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16", "21:9"
    ]] = Field("1:1",
        description="Controls the aspect ratio of the generated image. Default: 1:1"
    )
    
    width: Optional[int] = Field(None,
        ge=512,
        le=2048,
        description=(
            "Specifies the generated image width in pixels. Valid range: [512, 2048]. "
            "Values must be multiples of 8. Must be set together with height. "
            "If both width/height and aspect_ratio are provided, aspect_ratio takes priority"
        )
    )
    
    height: Optional[int] = Field(None,
        ge=512,
        le=2048,
        description=(
            "Specifies the generated image height in pixels. Valid range: [512, 2048]. "
            "Values must be multiples of 8. Must be set together with width. "
            "If both width/height and aspect_ratio are provided, aspect_ratio takes priority"
        )
    )
    
    response_format: Literal["url", "base64"] = Field("url",
        description="Controls the output format of the generated image. URL is valid for 24 hours"
    )
    
    seed: Optional[int] = Field(None,
        description=(
            "Random seed for reproducible results. If not provided, algorithm generates random seed. "
            "Same seed with identical parameters produces similar results"
        )
    )
    
    n: int = Field(1,
        ge=1,
        le=9,
        description="Controls the number of images generated per request. Value range: [1, 9]"
    )
    
    prompt_optimizer: bool = Field(False,
        description="Whether to enable automatic prompt optimization"
    )
