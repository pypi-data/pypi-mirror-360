from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class LittercoderBaseInput(BaseModel):
    """Base input model for Littercoder API."""
    mode: Optional[str] = Field(
        default="RELAX",
        description="RELAX for slow mode, FAST for fast mode"
    )
    notifyHook: Optional[str] = Field(
        default=None,
        description="Callback URL for notifications"
    )
    state: Optional[str] = Field(
        default=None,
        description="Custom state parameter"
    )


class LittercoderImagineInput(LittercoderBaseInput):
    """Input model for Littercoder imagine endpoint."""
    prompt: str = Field(
        ...,
        description="Text prompt for image generation"
    )
    base64Array: Optional[List[str]] = Field(
        default=None,
        description="Array of base64 encoded reference images"
    )


class LittercoderBlendInput(LittercoderBaseInput):
    """Input model for Littercoder blend endpoint."""
    base64Array: List[str] = Field(
        ...,
        description="Array of base64 encoded images to blend"
    )
    dimensions: Optional[str] = Field(
        default="SQUARE",
        description="Image dimensions: PORTRAIT, SQUARE, or LANDSCAPE"
    )


class LittercoderFaceSwapInput(LittercoderBaseInput):
    """Input model for Littercoder face swap endpoint."""
    sourceBase64: str = Field(
        ...,
        description="Base64 encoded source face image"
    )
    targetBase64: str = Field(
        ...,
        description="Base64 encoded target image"
    )


class LittercoderEditInput(LittercoderBaseInput):
    """Input model for Littercoder edit endpoint."""
    prompt: str = Field(
        ...,
        description="Text prompt for image editing"
    )
    imageBase64: str = Field(
        ...,
        description="Base64 encoded image to edit"
    )
    maskBase64: Optional[str] = Field(
        default=None,
        description="Base64 encoded mask image for selective editing"
    )


class LittercoderOutput(BaseModel):
    """Output model for Littercoder API responses."""
    code: int = Field(
        ...,
        description="Status code: 1 for success, others for errors"
    )
    description: str = Field(
        ...,
        description="Response description"
    )
    result: str = Field(
        ...,
        description="Task ID for the submitted job"
    )
