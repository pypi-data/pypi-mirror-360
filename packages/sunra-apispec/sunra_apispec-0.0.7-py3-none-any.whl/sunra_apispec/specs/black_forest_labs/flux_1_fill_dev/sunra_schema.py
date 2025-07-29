# Schema for Image-to-Image generation with Fill
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


class ImageToImageInput(BaseModel):
    """Input model for image-to-image generation with fill."""
    prompt: str = Field(
        default="",
        json_schema_extra={"x-sr-order": 200},
        description="The description of the changes you want to make. This text guides the inpainting process, allowing you to specify features, styles, or modifications for the masked area.",
    )
    number_of_steps: int = Field(
        default=30,  # Reduced number_of_steps for dev version
        ge=15,
        le=50,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 201},
        description="Number of steps for the image generation process",
    )
    guidance_scale: float = Field(
        default=40,  # Lower guidance_scale for dev version
        ge=2.0,
        le=100.0,
        multiple_of=0.1,
        json_schema_extra={"x-sr-order": 202},
        description="Guidance strength for the image generation process"
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 203},
        description="Optional seed for reproducibility"
    )
    image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="The image to inpaint. Can contain alpha mask. If the image width or height are not multiples of 32, they will be scaled to the closest multiple of 32. If the image dimensions don't fit within 1440x1440, it will be scaled down to fit."
    )
    mask_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 302},
        description="A black-and-white image that describes the part of the image to inpaint. Black areas will be preserved while white areas will be inpainted."
    )
    number_of_images: int = Field(
        default=1,
        ge=1,
        le=4,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 401},
        description="Number of outputs to generate."
    )
    megapixels: Literal["1", "0.25"] = Field(
        default="1",
        json_schema_extra={"x-sr-order": 402},
        description="Approximate number of megapixels for generated image",
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        json_schema_extra={"x-sr-order": 403},
        description="Output format for the generated image. Can be 'jpeg' or 'png'."
    )
    