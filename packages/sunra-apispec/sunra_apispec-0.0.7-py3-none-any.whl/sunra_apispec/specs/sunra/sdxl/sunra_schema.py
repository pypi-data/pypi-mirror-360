# Schema for Text-to-Image generation
from pydantic import BaseModel, Field

class TextToImageInput(BaseModel):
    """Input model for text-to-image generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        max_length=2500,
        description='The prompt for the image'
    )

    number_of_steps: int = Field(
        default=20,
        le=500,
        ge=1,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 201},
        description="The number of inference steps to use for the image generation."
    )
