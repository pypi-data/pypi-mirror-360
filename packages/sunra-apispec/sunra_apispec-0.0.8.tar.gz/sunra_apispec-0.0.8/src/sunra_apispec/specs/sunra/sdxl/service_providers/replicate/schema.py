from pydantic import BaseModel, Field


class ReplicateInput(BaseModel):
    """Input schema for SDXL model on Replicate."""
    prompt: str = Field(
        ...,
        description="The prompt to generate the image from."
    )

    num_inference_steps: int = Field(
        default=20,
        description="The number of inference steps to use for the image generation."
    )
