from enum import Enum
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field


class QueueStatusStatus(Enum):
    IN_QUEUE = "IN_QUEUE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class QueueStatus(BaseModel):
    """
    QueueStatus
    """
    status: QueueStatusStatus
    request_id: str = Field(..., description="The request id.")
    response_url: Optional[str] = Field(None, description="The response url.")
    status_url: Optional[str] = Field(None, description="The status url.")
    cancel_url: Optional[str] = Field(None, description="The cancel url.")
    logs: Optional[Dict[str, Any]] = Field(None, description="The logs.")
    metrics: Optional[Dict[str, Any]] = Field(None, description="The metrics.")
    queue_position: Optional[int] = Field(None, description="The queue position.")


class BriaBackgroundReplaceInput(BaseModel):
    """
    BGReplaceInput
    """
    image_url: str = Field(
        ...,
        examples=["https://storage.googleapis.com/falserverless/bria/bria_bg_replace_fg.jpg"],
        description="Input Image to erase from"
    )
    ref_image_url: Optional[str] = Field(
        "",
        examples=["https://storage.googleapis.com/falserverless/bria/bria_bg_replace_bg.jpg"],
        description=(
            'The URL of the reference image to be used for generating the new background. Use "" to leave empty. Either '
            "ref_image_url or bg_prompt has to be provided but not both. If both ref_image_url and ref_image_file "
            "are provided, ref_image_url will be used. Accepted formats are jpeg, jpg, png, webp."
        ),
        json_schema_extra={"x-order": 1}
    )
    prompt: Optional[str] = Field(
        None,
        examples=["Man leaning against a wall"],
        description="The prompt you would like to use to generate images.",
        json_schema_extra={"x-order": 2}
    )
    negative_prompt: Optional[str] = Field(
        "",
        description="The negative prompt you would like to use to generate images.",
        json_schema_extra={"x-order": 3}
    )
    refine_prompt: Optional[bool] = Field(
        True, description="Whether to refine prompt", json_schema_extra={"x-order": 4}
    )
    seed: Optional[int] = Field(
        None,
        ge=0,
        le=4294967295,
        description=(
            "The same seed and the same prompt given to the same version of the model\nwill output the same image every time."
        ),
        json_schema_extra={"x-order": 5}
    )
    fast: Optional[bool] = Field(
        True, description="Whether to use the fast model", json_schema_extra={"x-order": 6}
    )
    num_images: Optional[int] = Field(
        1,
        ge=1,
        le=4,
        description="Number of Images to generate.",
        json_schema_extra={"x-order": 7}
    )
    sync_mode: Optional[bool] = Field(
        False,
        description=(
            "\nIf set to true, the function will wait for the image to be generated and uploaded\nbefore returning the response. This will increase the latency of the function but\nit allows you to get the image directly in the response without going through the CDN.\n"
        ),
        json_schema_extra={"x-order": 8}
    )



class Image(BaseModel):
    """
    Represents an image file.
    """
    url: str = Field(..., description="The URL where the file can be downloaded from.")
    content_type: Optional[str] = Field(
        None,
        examples=["image/png"],
        description="The mime type of the file.",
        json_schema_extra={"x-order": 1}
    )
    file_name: Optional[str] = Field(
        None,
        examples=["z9RV14K95DvU.png"],
        description="The name of the file. It will be auto-generated if not provided.",
        json_schema_extra={"x-order": 2}
    )
    file_size: Optional[int] = Field(
        None,
        examples=[4404019],
        description="The size of the file in bytes.",
        json_schema_extra={"x-order": 3}
    )
    file_data: Optional[str] = Field(None, description="File data", json_schema_extra={"x-order": 4})
    width: Optional[int] = Field(
        None,
        examples=[1024],
        description="The width of the image in pixels.",
        json_schema_extra={"x-order": 5}
    )
    height: Optional[int] = Field(
        None,
        examples=[1024],
        description="The height of the image in pixels.",
        json_schema_extra={"x-order": 6}
    )



class BriaBackgroundReplaceOutput(BaseModel):
    """
    BGReplaceOutput
    """
    images: List[Image] = Field(
        ...,
        examples=[
            [
                {
                    "content_type": "image/png",
                    "url": "https://storage.googleapis.com/falserverless/bria/bria_bg_replace_res.jpg",
                }
            ]
        ],
        description="The generated images"
    )
    seed: int = Field(..., description="Seed value used for generation.")
