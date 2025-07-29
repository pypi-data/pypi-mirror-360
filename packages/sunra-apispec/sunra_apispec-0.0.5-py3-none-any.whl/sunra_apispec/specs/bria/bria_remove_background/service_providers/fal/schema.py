from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, HttpUrl


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


class BriaBackgroundRemoveInput(BaseModel):
    """
    BGRemoveInput
    """
    image_url: str = Field(
        ...,
        examples=["https://fal.media/files/panda/K5Rndvzmn1j-OI1VZXDVd.jpeg"],
        description="Input Image to erase from"
    )
    sync_mode: Optional[bool] = Field(
        False,
        description=(
            "If set to true, the function will wait for the image to be generated and uploaded before returning the response. This will increase the latency of the function but it allows you to get the image directly in the response without going through the CDN."
        ),
        json_schema_extra={"x-order": 1}
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
    

class BriaBackgroundRemoveOutput(BaseModel):
    """
    BGRemoveOutput
    """
    image: Image = Field(
        ...,
        examples=[
            {
                "file_size": 1076276,
                "height": 1024,
                "file_name": "070c731993e949d993c10ef6283d335d.png",
                "content_type": "image/png",
                "url": "https://v3.fal.media/files/tiger/GQEMNjRyxSoza7N8LPPqb_070c731993e949d993c10ef6283d335d.png",
                "width": 1024,
            }
        ],
        description="The generated image"
    )
