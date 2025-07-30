from pydantic import BaseModel, Field, HttpUrl

class BackgroundRemoveInput(BaseModel):
    image: HttpUrl | str = Field(
        ...,
        title="Image",
        description="Input Image to erase from",
        json_schema_extra={"x-sr-order": 301}
    )

