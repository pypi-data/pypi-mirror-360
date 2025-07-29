from pydantic import BaseModel, Field, HttpUrl
from typing import Literal, Union


class TextToImageInput(BaseModel):
    """Input model for text-to-image generation using GPT Image 1."""
    
    # Request & Model Configuration (100-700)
    openai_api_key: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 101},
        description="Your OpenAI API key. This model is only supported via your own key."
    )
    
    # Core Generation Input (200s)
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        min_length=1,
        max_length=32000,
        description="Text description of the desired image."
    )
    
    # Output Modality Specifications (400s)
    aspect_ratio: Literal["auto", "1:1", "3:2", "2:3"] = Field(
        "auto",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the generated image. Maps to sizes: 1024x1024 (1:1), 1536x1024 (3:2 landscape), 1024x1536 (2:3 portrait)."
    )
    
    background: Literal["transparent", "opaque", "auto"] = Field(
        "auto",
        json_schema_extra={"x-sr-order": 402},
        description="Background transparency setting. 'auto' lets the model decide, 'transparent' for transparent background, 'opaque' for solid background."
    )
    
    quality: Literal["high", "medium", "low"] = Field(
        "high",
        json_schema_extra={"x-sr-order": 403},
        description="The quality of the image that will be generated."
    )

    output_compression: int = Field(
        100,
        ge=0,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 404},
        description="The compression level (0-100%) for the generated images. This parameter is only supported for gpt-image-1 with the webp or jpeg output formats, and defaults to 100."
    )
    
    output_format: Literal["png", "jpeg", "webp"] = Field(
        "jpeg",
        json_schema_extra={"x-sr-order": 405},
        description="Output image format. Default: jpeg."
    )
    
    # Advanced & Model-Specific Controls (500s)
    user: str = Field(
        None,
        json_schema_extra={"x-sr-order": 501},
        description="Unique identifier for end-user to help monitor and detect abuse."
    )


class ImageEditingInput(BaseModel):
    """Input model for image editing using GPT Image 1."""
    
    # Request & Model Configuration (100-700)
    openai_api_key: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 101},
        description="Your OpenAI API key. This model is only supported via your own key."
    )
    
    # Core Generation Input (200s)
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        min_length=1,
        max_length=32000,
        description="Text description of the desired edit."
    )
    
    # Input Modality Parameters (300s)
    image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Image to edit. Must be a png, webp, or jpg file less than 25MB."
    )
    
    mask_image: HttpUrl | str = Field(
        None,
        json_schema_extra={"x-sr-order": 302},
        description="Mask image whose fully transparent areas indicate where the image should be edited. Must be a valid PNG file."
    )
    
    # Output Modality Specifications (400s)
    aspect_ratio: Literal["auto", "1:1", "3:2", "2:3"] = Field(
        "auto",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the generated image. Maps to sizes: 1024x1024 (1:1), 1536x1024 (3:2 landscape), 1024x1536 (2:3 portrait)."
    )
    
    background: Literal["transparent", "opaque", "auto"] = Field(
        "auto",
        json_schema_extra={"x-sr-order": 402},
        description="Background transparency setting. 'auto' lets the model decide, 'transparent' for transparent background, 'opaque' for solid background."
    )
    
    quality: Literal["high", "medium", "low"] = Field(
        "high",
        json_schema_extra={"x-sr-order": 403},
        description="The quality of the image that will be generated."
    )
    
    # Advanced & Model-Specific Controls (500s)
    user: str = Field(
        None,
        json_schema_extra={"x-sr-order": 501},
        description="Unique identifier for end-user to help monitor and detect abuse."
    )
