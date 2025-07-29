from pydantic import BaseModel, Field
from typing import Optional, Literal


class File(BaseModel):
    """File schema matching FAL API response format."""
    url: str = Field(..., description="The URL where the file can be downloaded from")
    content_type: Optional[str] = Field(None, description="The mime type of the file")
    file_name: Optional[str] = Field(None, description="The name of the file")
    file_size: Optional[int] = Field(None, description="The size of the file in bytes")


class KlingVideoV21ProImageToVideoInput(BaseModel):
    """Input schema for Kling V2.1 Pro Image-to-Video generation via FAL."""
    prompt: str = Field(..., max_length=2500, description="Text prompt for video generation")
    image_url: str = Field(..., description="URL of the image to be used for the video")
    duration: Literal["5", "10"] = Field("5", description="The duration of the generated video in seconds")
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field("16:9", description="The aspect ratio of the generated video frame")
    negative_prompt: Optional[str] = Field("blur, distort, and low quality", max_length=2500, description="Negative prompt")
    cfg_scale: float = Field(0.5, ge=0.0, le=1.0, description="The CFG (Classifier Free Guidance) scale")


class KlingVideoV21ProImageToVideoOutput(BaseModel):
    """Output schema for Kling V2.1 Pro Image-to-Video generation via FAL."""
    video: File = Field(..., description="The generated video") 