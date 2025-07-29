# Schema for Image-to-Image generation
from pydantic import BaseModel, Field, HttpUrl
from sunra_apispec.base.output_schema import ImageOutput

class ImageToImageInput(BaseModel):
    """Image to image input for HiDream E1 Full model"""

    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt for image generation"
    )
    
    negative_prompt: str = Field(
        None,
        json_schema_extra={"x-sr-order": 203},
        description="Negative prompt to avoid certain elements"
    )
    
    number_of_steps: int = Field(
        default=30,
        le=100,
        ge=10,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 204},
        description="Number of inference steps"
    )
    
    guidance_scale: float = Field(
        default=5.0,
        ge=0.0,
        le=10.0,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 205},
        description="Guidance scale for generation"
    )
    
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 206},
        description="Random seed for generation"
    )
    
    image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Input image to edit. Supports URL or base64 format"
    )
    
    image_guidance_scale: float = Field(
        default=4.0,
        ge=0.0,
        le=10.0,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 501},
        description="Image guidance scale"
    ) 

class HiDreamE1FullOutput(ImageOutput):
    predict_time: float = Field(
        ...,
        description="Time taken to generate the image",
    )
