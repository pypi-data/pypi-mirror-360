from typing import Literal, Optional
from pydantic import BaseModel, Field, HttpUrl

class ImageToImageInput(BaseModel):
    """
    Input for the model generation or image editing.
    """
    
    image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Image to use as reference. Must be jpeg, png, gif, or webp."
    )
    
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text description of what you want to generate, or the instruction on how to edit the given image."
    )
    
    aspect_ratio: Literal["None", "1:1", "2:3", "3:2", "3:4", "4:3", "16:9", "9:16", "21:9", "9:21"] = Field(
        "None",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the generated image. 'None' means follow the input image's aspect ratio."
    )
    
    number_of_steps: int = Field(
        28,
        ge=4,
        le=50,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 203},
        description="Number of inference steps"
    )
    
    guidance_scale: float = Field(
        2.5,
        ge=0,
        le=10,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 204},
        description="Guidance scale for generation"
    )
    
    seed: int = Field(
        None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 205},
        description="Random seed for reproducible generation. Leave blank for random."
    )
    
    output_format: Literal["webp", "jpg", "png"] = Field(
        "webp",
        json_schema_extra={"x-sr-order": 402},
        description="Output image format"
    )
    
    output_quality: int = Field(
        80,
        ge=0,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 403},
        description="Quality when saving the output images, from 0 to 100. 100 is best quality, 0 is lowest quality. Not relevant for .png outputs"
    )
    
    disable_safety_checker: bool = Field(
        False,
        json_schema_extra={"x-sr-order": 501},
        description="Disable NSFW safety checker"
    )
    
    fast_mode: bool = Field(
        True,
        json_schema_extra={"x-sr-order": 502},
        description="Make the model go fast, output quality may be slightly degraded for more difficult prompts"
    )