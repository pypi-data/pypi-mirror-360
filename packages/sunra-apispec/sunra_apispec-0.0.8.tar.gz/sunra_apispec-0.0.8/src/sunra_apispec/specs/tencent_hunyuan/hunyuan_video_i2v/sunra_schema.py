from pydantic import BaseModel, Field
from pydantic import HttpUrl

class ImageToVideoInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt describing the desired video.",
    )

    start_image: HttpUrl | str = Field(
        ...,
        title="Image",
        json_schema_extra={"x-sr-order": 202},
        description="Path to the image to use for video generation.",
    )
