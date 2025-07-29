# Schema for Recraft V2 Text-to-Image generation
from typing import Literal
from pydantic import BaseModel, Field

class TextToImageInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        max_length=1000,
        description="The prompt for the image generation"
    )
    aspect_ratio: Literal[
        "1:1", "4:3", "3:4", "16:9", "9:16"
    ] = Field(
        "1:1",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the image"
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
        json_schema_extra={"x-sr-order": 402},
        description="The style of the generated images"
    )
    style_id: str = Field(
        None,
        json_schema_extra={"x-sr-order": 403},
        description="The ID of the custom style reference (optional)"
    ) 