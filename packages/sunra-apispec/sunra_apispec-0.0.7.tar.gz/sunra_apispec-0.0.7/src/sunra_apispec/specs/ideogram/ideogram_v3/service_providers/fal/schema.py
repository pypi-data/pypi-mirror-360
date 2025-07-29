from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union


class File(BaseModel):
    """File output schema."""
    url: str = Field(description="The URL where the file can be downloaded from.")
    content_type: Optional[str] = Field(default=None, description="The mime type of the file.")
    file_name: Optional[str] = Field(default=None, description="The name of the file.")
    file_size: Optional[int] = Field(default=None, description="The size of the file in bytes.")


class ColorPaletteMember(BaseModel):
    """Color palette member."""
    color: str = Field(description="Hexadecimal color code")
    weight: Optional[float] = Field(default=None, description="Weight of the color")


class ColorPalette(BaseModel):
    """Color palette for generation."""
    name: Optional[str] = Field(default=None, description="Preset color palette name")
    members: Optional[List[ColorPaletteMember]] = Field(default=None, description="Custom color palette members")


# Text-to-Image Input Schema
class FalTextToImageInput(BaseModel):
    """FAL input schema for Ideogram V3 text-to-image generation."""
    
    prompt: str = Field(
        ...,
        description="Text prompt for image generation"
    )
    
    num_images: int = Field(
        default=1,
        description="Number of images to generate",
        ge=1,
        le=8
    )
    
    image_size: Optional[Union[Literal["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"], str]] = Field(
        default="square_hd",
        description="The resolution of the generated image"
    )
    
    style: Optional[Literal["AUTO", "GENERAL", "REALISTIC", "DESIGN"]] = Field(
        default=None,
        description="The style type to generate with"
    )
    
    expand_prompt: bool = Field(
        default=True,
        description="Determine if MagicPrompt should be used in generating the request or not"
    )
    
    rendering_speed: Literal["TURBO", "BALANCED", "QUALITY"] = Field(
        default="BALANCED",
        description="The rendering speed to use"
    )
    
    style_codes: Optional[List[str]] = Field(
        default=None,
        description="A list of 8 character hexadecimal codes representing the style of the image"
    )
    
    color_palette: Optional[ColorPalette] = Field(
        default=None,
        description="A color palette for generation"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Seed for the random number generator"
    )
    
    image_urls: Optional[List[str]] = Field(
        default=None,
        description="A set of images to use as style references"
    )


# Edit Input Schema
class FalEditInput(BaseModel):
    """FAL input schema for Ideogram V3 image editing."""
    
    prompt: str = Field(
        ...,
        description="The prompt to fill the masked part of the image"
    )
    
    image_url: str = Field(
        ...,
        description="The image URL to generate an image from"
    )
    
    mask_url: str = Field(
        ...,
        description="The mask URL to inpaint the image"
    )
    
    num_images: int = Field(
        default=1,
        description="Number of images to generate",
        ge=1,
        le=8
    )
    
    expand_prompt: bool = Field(
        default=True,
        description="Determine if MagicPrompt should be used in generating the request or not"
    )
    
    rendering_speed: Literal["TURBO", "BALANCED", "QUALITY"] = Field(
        default="BALANCED",
        description="The rendering speed to use"
    )
    
    style_codes: Optional[List[str]] = Field(
        default=None,
        description="A list of 8 character hexadecimal codes representing the style of the image"
    )
    
    color_palette: Optional[ColorPalette] = Field(
        default=None,
        description="A color palette for generation"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Seed for the random number generator"
    )
    
    image_urls: Optional[List[str]] = Field(
        default=None,
        description="A set of images to use as style references"
    )


# Reframe Input Schema
class FalReframeInput(BaseModel):
    """FAL input schema for Ideogram V3 image reframing."""
    
    image_url: str = Field(
        ...,
        description="The image URL to reframe"
    )
    
    image_size: Union[Literal["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"], str] = Field(
        ...,
        description="The resolution of the reframed image"
    )
    
    num_images: int = Field(
        default=1,
        description="Number of images to generate",
        ge=1,
        le=8
    )
    
    rendering_speed: Literal["TURBO", "BALANCED", "QUALITY"] = Field(
        default="BALANCED",
        description="The rendering speed to use"
    )
    
    style_codes: Optional[List[str]] = Field(
        default=None,
        description="A list of 8 character hexadecimal codes representing the style of the image"
    )
    
    color_palette: Optional[ColorPalette] = Field(
        default=None,
        description="A color palette for generation"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Seed for the random number generator"
    )
    
    image_urls: Optional[List[str]] = Field(
        default=None,
        description="A set of images to use as style references"
    )


# Remix Input Schema
class FalRemixInput(BaseModel):
    """FAL input schema for Ideogram V3 image remixing."""
    
    image_url: str = Field(
        ...,
        description="The image URL to remix"
    )
    
    prompt: Optional[str] = Field(
        default=None,
        description="Text prompt for image remixing"
    )
    
    image_size: Optional[Union[Literal["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"], str]] = Field(
        default="square_hd",
        description="The resolution of the remixed image"
    )
    
    num_images: int = Field(
        default=1,
        description="Number of images to generate",
        ge=1,
        le=8
    )
    
    expand_prompt: bool = Field(
        default=True,
        description="Determine if MagicPrompt should be used in generating the request or not"
    )
    
    rendering_speed: Literal["TURBO", "BALANCED", "QUALITY"] = Field(
        default="BALANCED",
        description="The rendering speed to use"
    )
    
    style: Optional[Literal["AUTO", "GENERAL", "REALISTIC", "DESIGN"]] = Field(
        default=None,
        description="The style type to generate with"
    )
    
    style_codes: Optional[List[str]] = Field(
        default=None,
        description="A list of 8 character hexadecimal codes representing the style of the image"
    )
    
    color_palette: Optional[ColorPalette] = Field(
        default=None,
        description="A color palette for generation"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Seed for the random number generator"
    )
    
    image_urls: Optional[List[str]] = Field(
        default=None,
        description="A set of images to use as style references"
    )
    
    image_strength: Optional[float] = Field(
        default=None,
        description="Strength of the input image in the remix process",
        ge=0.0,
        le=1.0
    )


# Replace Background Input Schema
class FalReplaceBackgroundInput(BaseModel):
    """FAL input schema for Ideogram V3 background replacement."""
    
    image_url: str = Field(
        ...,
        description="The image URL for background replacement"
    )
    
    prompt: Optional[str] = Field(
        default=None,
        description="Text prompt for background replacement"
    )
    
    num_images: int = Field(
        default=1,
        description="Number of images to generate",
        ge=1,
        le=8
    )
    
    expand_prompt: bool = Field(
        default=True,
        description="Determine if MagicPrompt should be used in generating the request or not"
    )
    
    rendering_speed: Literal["TURBO", "BALANCED", "QUALITY"] = Field(
        default="BALANCED",
        description="The rendering speed to use"
    )
    
    style_codes: Optional[List[str]] = Field(
        default=None,
        description="A list of 8 character hexadecimal codes representing the style of the image"
    )
    
    color_palette: Optional[ColorPalette] = Field(
        default=None,
        description="A color palette for generation"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Seed for the random number generator"
    )
    
    image_urls: Optional[List[str]] = Field(
        default=None,
        description="A set of images to use as style references"
    )


# Common Output Schema
class FalIdeogramV3Output(BaseModel):
    """FAL output schema for Ideogram V3 operations."""
    images: List[File] = Field(description="Generated images")
    seed: int = Field(description="Seed used for the random number generator") 