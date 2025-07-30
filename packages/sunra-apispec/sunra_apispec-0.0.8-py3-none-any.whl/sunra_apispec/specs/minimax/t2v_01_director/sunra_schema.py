# Schema for Text-to-Image generation
from pydantic import BaseModel, Field

class TextToVideoInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        max_length=2500,
        description="The prompt for the video"
    )
    prompt_enhancer: bool = Field(
        True,
        json_schema_extra={"x-sr-order": 201},
        description="Whether to use the model's prompt optimizer"
    )
