# Schema for Recraft V2 FAL service provider
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


class ImageSize(BaseModel):
    """Custom image size specification."""
    width: int = Field(
        512,
        gt=0,
        le=14142,
        description="The width of the generated image."
    )
    height: int = Field(
        512,
        gt=0,
        le=14142,
        description="The height of the generated image."
    )


class RGBColor(BaseModel):
    """RGB color specification."""
    r: int = Field(
        0,
        ge=0,
        le=255,
        description="Red color value"
    )
    g: int = Field(
        0,
        ge=0,
        le=255,
        description="Green color value"
    )
    b: int = Field(
        0,
        ge=0,
        le=255,
        description="Blue color value"
    )


class RecraftV2TextToImageInput(BaseModel):
    """Input schema for Recraft V2 text-to-image generation via FAL."""
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The prompt for image generation"
    )
    image_size: Union[ImageSize, Literal[
        "square_hd", "square", "portrait_4_3", "portrait_16_9",
        "landscape_4_3", "landscape_16_9"
    ]] = Field(
        "square_hd",
        description="Image size specification"
    )
    enable_safety_checker: bool = Field(
        False,
        description="If set to true, the safety checker will be enabled."
    )
    colors: List[RGBColor] = Field(
        default_factory=list,
        description="An array of preferable colors"
    )
    style: Literal[
        "any", "realistic_image", "digital_illustration", "vector_illustration",
        "realistic_image/b_and_w", "realistic_image/enterprise", "realistic_image/hard_flash",
        "realistic_image/hdr", "realistic_image/motion_blur", "realistic_image/natural_light",
        "realistic_image/studio_portrait", "digital_illustration/2d_art_poster",
        "digital_illustration/2d_art_poster_2", "digital_illustration/3d",
        "digital_illustration/80s", "digital_illustration/engraving_color",
        "digital_illustration/glow", "digital_illustration/grain",
        "digital_illustration/hand_drawn", "digital_illustration/hand_drawn_outline",
        "digital_illustration/handmade_3d", "digital_illustration/infantile_sketch",
        "digital_illustration/kawaii", "digital_illustration/pixel_art",
        "digital_illustration/psychedelic", "digital_illustration/seamless",
        "digital_illustration/voxel", "digital_illustration/watercolor",
        "vector_illustration/cartoon", "vector_illustration/doodle_line_art",
        "vector_illustration/engraving", "vector_illustration/flat_2",
        "vector_illustration/kawaii", "vector_illustration/line_art",
        "vector_illustration/line_circuit", "vector_illustration/linocut",
        "vector_illustration/seamless", "icon/broken_line", "icon/colored_outline",
        "icon/colored_shapes", "icon/colored_shapes_gradient", "icon/doodle_fill",
        "icon/doodle_offset_fill", "icon/offset_fill", "icon/outline",
        "icon/outline_gradient", "icon/uneven_fill"
    ] = Field(
        "realistic_image",
        description="The style of the generated images. Vector images cost 2X as much."
    )
    style_id: Optional[str] = Field(
        None,
        description="The ID of the custom style reference (optional)"
    )


class File(BaseModel):
    """File output specification."""
    url: str = Field(
        ...,
        description="The URL where the file can be downloaded from."
    )
    content_type: Optional[str] = Field(
        None,
        description="The mime type of the file."
    )
    file_name: Optional[str] = Field(
        None,
        description="The name of the file. It will be auto-generated if not provided."
    )
    file_size: Optional[int] = Field(
        None,
        description="The size of the file in bytes."
    )
    file_data: Optional[str] = Field(
        None,
        description="File data"
    )


class RecraftV2TextToImageOutput(BaseModel):
    """Output schema for Recraft V2 text-to-image generation via FAL."""
    images: List[File] = Field(
        ...,
        description="Generated images"
    ) 