from pydantic import BaseModel, Field, HttpUrl


class UpscaleInput(BaseModel):
    """
    UpscaleInput
    """

    image: HttpUrl | str = Field(
        ...,
        description="The URL of the image to be upscaled. Must be in PNG format.",
        json_schema_extra={"x-sr-order": 301}
    )

