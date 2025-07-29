from typing import Literal, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class MegapixelsEnum(str, Enum):
    """Enum for megapixels options."""
    ONE = "1"
    QUARTER = "0.25"
    MATCH_INPUT = "match_input"


class OutputFormatEnum(str, Enum):
    """Enum for output format options."""
    WEBP = "webp"
    JPG = "jpg"
    PNG = "png"


class ReplicateInput(BaseModel):
    """Input model for Replicate FLUX.1-Fill-Dev API."""
    prompt: str = Field(
        ...,
        description="Prompt for generated image"
    )
    image: str = Field(
        ...,
        description="The image to inpaint. Can contain alpha mask. If the image width or height are not multiples of 32, they will be scaled to the closest multiple of 32. If the image dimensions don't fit within 1440x1440, it will be scaled down to fit."
    )
    mask: Optional[str] = Field(
        default=None,
        description="A black-and-white image that describes the part of the image to inpaint. Black areas will be preserved while white areas will be inpainted."
    )
    num_outputs: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of outputs to generate"
    )
    num_inference_steps: int = Field(
        default=28,
        ge=1,
        le=50,
        description="Number of denoising steps. Recommended range is 28-50, and lower number of steps produce lower quality outputs, faster."
    )
    guidance: float = Field(
        default=30,
        ge=0,
        le=100,
        description="Guidance for generated image"
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
    lora_weights: Optional[str] = Field(
        default=None,
        description="Load LoRA weights. Supports Replicate models in the format <owner>/<username> or <owner>/<username>/<version>, HuggingFace URLs in the format huggingface.co/<owner>/<model-name>, CivitAI URLs in the format civitai.com/models/<id>[/<model-name>], or arbitrary .safetensors URLs from the Internet. For example, 'fofr/flux-pixar-cars'"
    )
    lora_scale: float = Field(
        default=1,
        ge=-1,
        le=3,
        description="Determines how strongly the main LoRA should be applied. Sane results between 0 and 1 for base inference. For go_fast we apply a 1.5x multiplier to this value; we've generally seen good performance when scaling the base value by that amount. You may still need to experiment to find the best value for your particular lora."
    )
    disable_safety_checker: bool = Field(
        default=False,
        description="Disable safety checker for generated images."
    )
    megapixels: MegapixelsEnum = Field(
        default=MegapixelsEnum.ONE,
        description="Approximate number of megapixels for generated image. Use match_input to match the size of the input (with an upper limit of 1440x1440 pixels)"
    )


class ReplicateOutput(BaseModel):
    """Output model for Replicate FLUX.1-Fill-Dev API."""
    output: List[str] = Field(
        ...,
        description="List of generated image URLs"
    )
    