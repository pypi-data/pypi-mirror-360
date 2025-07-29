from typing import Literal, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class MegapixelsEnum(str, Enum):
    """Enum for megapixels options."""
    ONE = "1"
    QUARTER = "0.25"


class OutputFormatEnum(str, Enum):
    """Enum for output format options."""
    WEBP = "webp"
    JPG = "jpg"
    PNG = "png"


class AspectRatioEnum(str, Enum):
    """Enum for aspect ratio options."""
    SQUARE = "1:1"
    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    LANDSCAPE_21_9 = "21:9"
    PORTRAIT_9_21 = "9:21"
    LANDSCAPE_3_2 = "3:2"
    PORTRAIT_2_3 = "2:3"
    LANDSCAPE_4_5 = "4:5"
    PORTRAIT_5_4 = "5:4"
    LANDSCAPE_3_4 = "3:4"
    PORTRAIT_4_3 = "4:3"


class ReplicateInput(BaseModel):
    """Input model for Replicate FLUX.1-Schnell API."""
    prompt: str = Field(
        ...,
        description="Prompt for generated image"
    )
    aspect_ratio: AspectRatioEnum = Field(
        default=AspectRatioEnum.SQUARE,
        description="Aspect ratio for the generated image"
    )
    num_outputs: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of outputs to generate"
    )
    num_inference_steps: int = Field(
        default=4,
        ge=1,
        le=4,
        description="Number of denoising steps. 4 is recommended, and lower number of steps produce lower quality outputs, faster."
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed. Set for reproducible generation"
    )
    output_format: OutputFormatEnum = Field(
        default=OutputFormatEnum.WEBP,
        description="Format of the output images"
    )
    output_quality: int = Field(
        default=80,
        ge=0,
        le=100,
        description="Quality when saving the output images, from 0 to 100. 100 is best quality, 0 is lowest quality. Not relevant for .png outputs"
    )
    disable_safety_checker: bool = Field(
        default=False,
        description="Disable safety checker for generated images."
    )
    go_fast: bool = Field(
        default=True,
        description="Run faster predictions with model optimized for speed (currently fp8 quantized); disable to run in original bf16"
    )
    megapixels: MegapixelsEnum = Field(
        default=MegapixelsEnum.ONE,
        description="Approximate number of megapixels for generated image"
    )


class ReplicateOutput(BaseModel):
    """Output model for Replicate FLUX.1-Schnell API."""
    output: List[str] = Field(
        ...,
        description="List of generated image URLs"
    ) 