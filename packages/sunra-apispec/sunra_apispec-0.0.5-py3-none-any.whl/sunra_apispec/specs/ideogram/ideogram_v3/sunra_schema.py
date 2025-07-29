from pydantic import BaseModel, Field, HttpUrl
from typing import List, Literal


class TextToImageInput(BaseModel):
    """Input schema for Ideogram V3 text-to-image generation."""
    
    prompt: str = Field(
        ...,
        description="Text prompt for image generation",
        json_schema_extra={"x-sr-order": 201}
    )
    
    negative_prompt: str = Field(
        default=None,
        description="Description of what to exclude from an image.",
        json_schema_extra={"x-sr-order": 203}
    )
    
    prompt_enhancer: bool = Field(
        default=True,
        description="Whether to enhance the prompt automatically",
        json_schema_extra={"x-sr-order": 202}
    )

    number_of_images: int = Field(
        default=1,
        le=8,
        ge=1,
        multiple_of=1,
        description="Number of images to generate",
        json_schema_extra={"x-sr-order": 205}
    )
    
    aspect_ratio: Literal[
        "1:1", "4:3", "3:4",
        "16:9", "9:16"
    ] = Field(
        default="16:9",
        description="Aspect ratio for the generated image",
        json_schema_extra={"x-sr-order": 401}
    )
    
    rendering_speed: Literal["turbo", "default", "quality"] = Field(
        default="default",
        description="Rendering speed mode",
        json_schema_extra={"x-sr-order": 402}
    )
    
    style_type: Literal["auto", "general", "realistic", "design"] = Field(
        default="general",
        description="Type of style to apply",
        json_schema_extra={"x-sr-order": 406}
    )

    style_codes: List[str] = Field(
        default=None,
        description="A list of 8 character hexadecimal codes representing the style of the image. Cannot be used in conjunction with style_reference_images or style_type",
        json_schema_extra={"x-sr-order": 405}
    )
    
    style_reference_images: List[HttpUrl | str] = Field(
        default=None,
        description="Reference images for style transfer",
        json_schema_extra={"x-sr-order": 407}
    )


class EditInput(BaseModel):
    """Input schema for Ideogram V3 image editing."""
    
    prompt: str = Field(
        ...,
        description="Text prompt for image editing",
        json_schema_extra={"x-sr-order": 201}
    )
    
    prompt_enhancer: bool = Field(
        default=None,
        description="Whether to enhance the prompt automatically",
        json_schema_extra={"x-sr-order": 202}
    )

    number_of_images: int = Field(
        default=1,
        le=8,
        ge=1,
        multiple_of=1,
        description="Number of images to generate",
        json_schema_extra={"x-sr-order": 205}
    )
    
    image: HttpUrl | str = Field(
        ...,
        description="URL of the image to edit",
        json_schema_extra={"x-sr-order": 301}
    )
    
    mask_image: HttpUrl | str = Field(
        ...,
        description="URL of the mask image for selective editing",
        json_schema_extra={"x-sr-order": 302}
    )
    
    rendering_speed: Literal["turbo", "default", "quality"] = Field(
        default="default",
        description="Rendering speed mode",
        json_schema_extra={"x-sr-order": 401}
    )
    
    style_codes: List[str] = Field(
        default=None,
        description="A list of 8 character hexadecimal codes representing the style of the image. Cannot be used in conjunction with style_reference_images or style_type",
        json_schema_extra={"x-sr-order": 405}
    )
    
    style_reference_images: List[HttpUrl | str] = Field(
        default=None,
        description="Reference images for style transfer",
        json_schema_extra={"x-sr-order": 407}
    )


class ReframeInput(BaseModel):
    """Input schema for Ideogram V3 image reframing."""
    
    image: HttpUrl | str = Field(
        ...,
        description="URL of the image to reframe",
        json_schema_extra={"x-sr-order": 301}
    )
    
    number_of_images: int = Field(
        default=1,
        le=8,
        ge=1,
        multiple_of=1,
        description="Number of images to generate",
        json_schema_extra={"x-sr-order": 205}
    )

    aspect_ratio: Literal[
        "1:1", "4:3", "3:4",
        "16:9", "9:16"
    ] = Field(
        ...,
        description="Aspect ratio for the generated image",
        json_schema_extra={"x-sr-order": 401}
    )

    rendering_speed: Literal["turbo", "default", "quality"] = Field(
        default="default",
        description="Rendering speed mode",
        json_schema_extra={"x-sr-order": 402}
    )
    
    style_codes: List[str] = Field(
        default=None,
        description="A list of 8 character hexadecimal codes representing the style of the image. Cannot be used in conjunction with style_reference_images or style_type",
        json_schema_extra={"x-sr-order": 405}
    )
    
    style_reference_images: List[HttpUrl | str] = Field(
        default=None,
        description="Reference images for style transfer",
        json_schema_extra={"x-sr-order": 407}
    )


class RemixInput(BaseModel):
    """Input schema for Ideogram V3 image remixing."""
    
    prompt: str = Field(
        ...,
        description="Text prompt for image remixing",
        json_schema_extra={"x-sr-order": 201}
    )
    
    prompt_enhancer: bool = Field(
        default=None,
        description="Whether to enhance the prompt automatically",
        json_schema_extra={"x-sr-order": 202}
    )

    negative_prompt: str = Field(
        default=None,
        description="Description of what to exclude from an image",
        json_schema_extra={"x-sr-order": 203}
    )

    number_of_images: int = Field(
        default=1,
        le=8,
        ge=1,
        multiple_of=1,
        description="Number of images to generate",
        json_schema_extra={"x-sr-order": 205}
    )
    
    image: HttpUrl | str = Field(
        ...,
        description="URL of the image to remix",
        json_schema_extra={"x-sr-order": 301}
    )
    
    image_strength: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        multiple_of=0.01,
        description="Strength of the input image in the remix process",
        json_schema_extra={"x-sr-order": 303}
    )
    
    aspect_ratio: Literal[
        "1:1", "4:3", "3:4",
        "16:9", "9:16"
    ] = Field(
        default="1:1",
        description="Aspect ratio for the remixed image",
        json_schema_extra={"x-sr-order": 401}
    )
    
    rendering_speed: Literal["turbo", "default", "quality"] = Field(
        default="default",
        description="Rendering speed mode",
        json_schema_extra={"x-sr-order": 402}
    )
    
    style_codes: List[str] = Field(
        default=None,
        description="A list of 8 character hexadecimal codes representing the style of the image. Cannot be used in conjunction with style_reference_images or style_type",
        json_schema_extra={"x-sr-order": 405}
    )
    
    style_type: Literal["auto", "general", "realistic", "design"] = Field(
        default="general",
        description="Type of style to apply",
        json_schema_extra={"x-sr-order": 406}
    )
    
    style_reference_images: List[HttpUrl | str] = Field(
        default=None,
        description="Reference images for style transfer",
        json_schema_extra={"x-sr-order": 407}
    )


class ReplaceBackgroundInput(BaseModel):
    """Input schema for Ideogram V3 background replacement."""
    
    prompt: str = Field(
        ...,
        description="Text prompt for background replacement",
        json_schema_extra={"x-sr-order": 201}
    )
    
    prompt_enhancer: bool = Field(
        default=None,
        description="Whether to enhance the prompt automatically",
        json_schema_extra={"x-sr-order": 202}
    )

    number_of_images: int = Field(
        default=1,
        le=8,
        ge=1,
        multiple_of=1,
        description="Number of images to generate",
        json_schema_extra={"x-sr-order": 205}
    )
    
    image: HttpUrl | str = Field(
        ...,
        description="URL of the image for background replacement",
        json_schema_extra={"x-sr-order": 301}
    )
    
    rendering_speed: Literal["turbo", "default", "quality"] = Field(
        default="default",
        description="Rendering speed mode",
        json_schema_extra={"x-sr-order": 401}
    )
    
    style_codes: List[str] = Field(
        default=None,
        description="A list of 8 character hexadecimal codes representing the style of the image. Cannot be used in conjunction with style_reference_images or style_type",
        json_schema_extra={"x-sr-order": 402}
    )
    
    style_reference_images: List[HttpUrl | str] = Field(
        default=None,
        description="Reference images for style transfer",
        json_schema_extra={"x-sr-order": 403}
    ) 
