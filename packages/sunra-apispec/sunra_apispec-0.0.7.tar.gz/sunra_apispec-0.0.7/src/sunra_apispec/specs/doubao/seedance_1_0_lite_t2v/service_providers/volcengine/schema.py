# Schema for Volcengine Video Generation API
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class ImageUrl(BaseModel):
    """Image URL structure for image content"""
    url: str = Field(
        ...,
        description="URL of the image to use for video generation"
    )


class TextContent(BaseModel):
    """Text content structure"""
    type: Literal["text"] = Field(
        default="text",
        description="Content type, must be 'text'"
    )
    text: str = Field(
        ...,
        description=(
            "Text content for video generation, including prompt and optional parameters. "
            "Format: 'prompt text --[parameter_name value]'. "
            "Supported parameters: resolution (rs), ratio (rt), duration (dur), "
            "framepersecond (fps), watermark (wm), seed, camerafixed (cf)"
        )
    )


class ImageContent(BaseModel):
    """Image content structure for image-to-video generation"""
    type: Literal["image_url"] = Field(
        default="image_url",
        description="Content type, must be 'image_url'"
    )
    image_url: ImageUrl = Field(
        ...,
        description="Image URL information"
    )


class VolcengineTextToVideoInput(BaseModel):
    """Input schema for Volcengine text-to-video generation"""
    
    model: str = Field(
        ...,
        description=(
            "Model ID to use for video generation. "
            "Supported models: doubao-seedance-1-0-lite-t2v, doubao-seaweed, wan2-1-14b-t2v"
        ),
        examples=["doubao-seedance-1-0-lite-t2v-250428"]
    )
    
    content: List[TextContent] = Field(
        ...,
        min_items=1,
        description="Array of text content for video generation"
    )


class VolcengineVideoGenResponse(BaseModel):
    """Response schema for Volcengine video generation"""
    
    id: str = Field(
        ...,
        description="Video generation task ID for querying, canceling, or deleting the task"
    )


# Text command parameters documentation for reference
class TextCommandParameters(BaseModel):
    """
    Text command parameters that can be appended to the prompt text.
    Format: 'prompt text --[parameter_name value]'
    
    These are not separate fields but are embedded in the text content as command parameters.
    """
    
    resolution: Literal["480p", "720p"] = Field(
        default="720p",
        description="Video resolution (480p or 720p). Short form: rs"
    )
    
    ratio: Literal["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "9:21", "keep_ratio", "adaptive"] = Field(
        default="16:9",
        description=(
            "Video aspect ratio. Default varies by model: "
            "16:9 for most models, keep_ratio for wan2.1-14b-i2v, "
            "adaptive for doubao-seaweed and doubao-seedance i2v. Short form: rt"
        )
    )
    
    duration: Literal[5, 10] = Field(
        default=5,
        description="Video duration in seconds (5 or 10). Short form: dur"
    )
    
    framepersecond: Literal[16, 24] = Field(
        default=16,
        description=(
            "Frame rate (16 or 24 fps). Default: 16 for wan2.1-14b, "
            "24 for doubao-seaweed. Short form: fps"
        )
    )
    
    watermark: Optional[bool] = Field(
        default=False,
        description="Whether to include watermark (true/false). Short form: wm"
    )
    
    seed: Optional[int] = Field(
        default=-1,
        ge=-1,
        le=2**32-1,
        description=(
            "Random seed for controllable generation. "
            "Range: [-1, 2^32-1]. -1 means random seed"
        )
    )
    
    camerafixed: Optional[bool] = Field(
        default=False,
        description=(
            "Whether to fix camera position (true/false). "
            "When true, adds camera fixing instruction to prompt. Short form: cf"
        )
    )
