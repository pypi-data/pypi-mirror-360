# Schema for Recraft V3 FAL service provider
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


class RecraftV3TextToImageInput(BaseModel):
    """Input schema for Recraft V3 text-to-image generation via FAL."""
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
        "realistic_image/b_and_w", "realistic_image/hard_flash", "realistic_image/hdr",
        "realistic_image/natural_light", "realistic_image/studio_portrait",
        "realistic_image/enterprise", "realistic_image/motion_blur",
        "realistic_image/evening_light", "realistic_image/faded_nostalgia",
        "realistic_image/forest_life", "realistic_image/mystic_naturalism",
        "realistic_image/natural_tones", "realistic_image/organic_calm",
        "realistic_image/real_life_glow", "realistic_image/retro_realism",
        "realistic_image/retro_snapshot", "realistic_image/urban_drama",
        "realistic_image/village_realism", "realistic_image/warm_folk",
        "digital_illustration/pixel_art", "digital_illustration/hand_drawn",
        "digital_illustration/grain", "digital_illustration/infantile_sketch",
        "digital_illustration/2d_art_poster", "digital_illustration/handmade_3d",
        "digital_illustration/hand_drawn_outline", "digital_illustration/engraving_color",
        "digital_illustration/2d_art_poster_2", "digital_illustration/antiquarian",
        "digital_illustration/bold_fantasy", "digital_illustration/child_book",
        "digital_illustration/child_books", "digital_illustration/cover",
        "digital_illustration/crosshatch", "digital_illustration/digital_engraving",
        "digital_illustration/expressionism", "digital_illustration/freehand_details",
        "digital_illustration/grain_20", "digital_illustration/graphic_intensity",
        "digital_illustration/hard_comics", "digital_illustration/long_shadow",
        "digital_illustration/modern_folk", "digital_illustration/multicolor",
        "digital_illustration/neon_calm", "digital_illustration/noir",
        "digital_illustration/nostalgic_pastel", "digital_illustration/outline_details",
        "digital_illustration/pastel_gradient", "digital_illustration/pastel_sketch",
        "digital_illustration/pop_art", "digital_illustration/pop_renaissance",
        "digital_illustration/street_art", "digital_illustration/tablet_sketch",
        "digital_illustration/urban_glow", "digital_illustration/urban_sketching",
        "digital_illustration/vanilla_dreams", "digital_illustration/young_adult_book",
        "digital_illustration/young_adult_book_2", "vector_illustration/bold_stroke",
        "vector_illustration/chemistry", "vector_illustration/colored_stencil",
        "vector_illustration/contour_pop_art", "vector_illustration/cosmics",
        "vector_illustration/cutout", "vector_illustration/depressive",
        "vector_illustration/editorial", "vector_illustration/emotional_flat",
        "vector_illustration/infographical", "vector_illustration/marker_outline",
        "vector_illustration/mosaic", "vector_illustration/naivector",
        "vector_illustration/roundish_flat", "vector_illustration/segmented_colors",
        "vector_illustration/sharp_contrast", "vector_illustration/thin",
        "vector_illustration/vector_photo", "vector_illustration/vivid_shapes",
        "vector_illustration/engraving", "vector_illustration/line_art",
        "vector_illustration/line_circuit", "vector_illustration/linocut"
    ] = Field(
        "realistic_image",
        description="The style of the generated images. Vector images cost 2X as much."
    )
    style_id: Optional[str] = Field(
        None,
        description="The ID of the custom style reference (optional)"
    )


class RecraftV3ImageToImageInput(BaseModel):
    """Input schema for Recraft V3 image-to-image generation via FAL."""
    prompt: str = Field(
        ...,
        max_length=1000,
        description="A text description of areas to change."
    )
    style: Literal[
        "any", "realistic_image", "digital_illustration", "vector_illustration",
        "realistic_image/b_and_w", "realistic_image/hard_flash", "realistic_image/hdr",
        "realistic_image/natural_light", "realistic_image/studio_portrait",
        "realistic_image/enterprise", "realistic_image/motion_blur",
        "realistic_image/evening_light", "realistic_image/faded_nostalgia",
        "realistic_image/forest_life", "realistic_image/mystic_naturalism",
        "realistic_image/natural_tones", "realistic_image/organic_calm",
        "realistic_image/real_life_glow", "realistic_image/retro_realism",
        "realistic_image/retro_snapshot", "realistic_image/urban_drama",
        "realistic_image/village_realism", "realistic_image/warm_folk",
        "digital_illustration/pixel_art", "digital_illustration/hand_drawn",
        "digital_illustration/grain", "digital_illustration/infantile_sketch",
        "digital_illustration/2d_art_poster", "digital_illustration/handmade_3d",
        "digital_illustration/hand_drawn_outline", "digital_illustration/engraving_color",
        "digital_illustration/2d_art_poster_2", "digital_illustration/antiquarian",
        "digital_illustration/bold_fantasy", "digital_illustration/child_book",
        "digital_illustration/child_books", "digital_illustration/cover",
        "digital_illustration/crosshatch", "digital_illustration/digital_engraving",
        "digital_illustration/expressionism", "digital_illustration/freehand_details",
        "digital_illustration/grain_20", "digital_illustration/graphic_intensity",
        "digital_illustration/hard_comics", "digital_illustration/long_shadow",
        "digital_illustration/modern_folk", "digital_illustration/multicolor",
        "digital_illustration/neon_calm", "digital_illustration/noir",
        "digital_illustration/nostalgic_pastel", "digital_illustration/outline_details",
        "digital_illustration/pastel_gradient", "digital_illustration/pastel_sketch",
        "digital_illustration/pop_art", "digital_illustration/pop_renaissance",
        "digital_illustration/street_art", "digital_illustration/tablet_sketch",
        "digital_illustration/urban_glow", "digital_illustration/urban_sketching",
        "digital_illustration/vanilla_dreams", "digital_illustration/young_adult_book",
        "digital_illustration/young_adult_book_2", "vector_illustration/bold_stroke",
        "vector_illustration/chemistry", "vector_illustration/colored_stencil",
        "vector_illustration/contour_pop_art", "vector_illustration/cosmics",
        "vector_illustration/cutout", "vector_illustration/depressive",
        "vector_illustration/editorial", "vector_illustration/emotional_flat",
        "vector_illustration/infographical", "vector_illustration/marker_outline",
        "vector_illustration/mosaic", "vector_illustration/naivector",
        "vector_illustration/roundish_flat", "vector_illustration/segmented_colors",
        "vector_illustration/sharp_contrast", "vector_illustration/thin",
        "vector_illustration/vector_photo", "vector_illustration/vivid_shapes",
        "vector_illustration/engraving", "vector_illustration/line_art",
        "vector_illustration/line_circuit", "vector_illustration/linocut"
    ] = Field(
        "realistic_image",
        description="The style of the generated images. Vector images cost 2X as much."
    )
    style_id: Optional[str] = Field(
        None,
        description="The ID of the custom style reference (optional)"
    )
    image_url: str = Field(
        ...,
        min_length=1,
        max_length=2083,
        description="The URL of the image to modify. Must be less than 5 MB in size, have resolution less than 16 MP and max dimension less than 4096 pixels."
    )
    strength: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Defines the difference with the original image, should lie in [0, 1], where 0 means almost identical, and 1 means miserable similarity"
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


class RecraftV3TextToImageOutput(BaseModel):
    """Output schema for Recraft V3 text-to-image generation via FAL."""
    images: List[File] = Field(
        ...,
        description="Generated images"
    )


class RecraftV3ImageToImageOutput(BaseModel):
    """Output schema for Recraft V3 image-to-image generation via FAL."""
    images: List[File] = Field(
        ...,
        description="Generated images"
    ) 