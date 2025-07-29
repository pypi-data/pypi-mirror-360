from pydantic import BaseModel, Field, HttpUrl


class UpscaleInput(BaseModel):
    """Input schema for Ideogram upscale."""
    
    image: HttpUrl | str = Field(
        ...,
        description="URL of the image to upscale",
        json_schema_extra={"x-sr-order": 301}
    )
    
    prompt: str = Field(
        default=None,
        description="Text prompt to guide the upscaling process",
        json_schema_extra={"x-sr-order": 201}
    )
    
    prompt_enhancer: bool = Field(
        default=True,
        description="Whether to enhance the prompt automatically",
        json_schema_extra={"x-sr-order": 202}
    )
    
    resemblance: int = Field(
        default=50,
        description="The resemblance of the upscaled image to the original image",
        ge=1,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 401}
    )
    
    detail: int = Field(
        default=50,
        description="The detail of the upscaled image",
        ge=1,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 402}
    )