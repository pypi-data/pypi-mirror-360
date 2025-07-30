from pydantic import BaseModel, Field, HttpUrl

class BackgroundReplaceInput(BaseModel):
    image: HttpUrl | str = Field(
        ...,
        title="Image",
        description="Input Image to erase from",
        json_schema_extra={"x-sr-order": 301}
    )
    reference_image: HttpUrl | str = Field(
        None,
        description=(
            'The URL of the reference image to be used for generating the new background. Use "" to leave empty. Either '
            "ref_image_url or bg_prompt has to be provided but not both. If both ref_image_url and ref_image_file "
            "are provided, ref_image_url will be used. Accepted formats are jpeg, jpg, png, webp."
        ),
        json_schema_extra={"x-sr-order": 302}
    )
    prompt: str = Field(
        None,
        description="The prompt you would like to use to generate images.",
        json_schema_extra={"x-sr-order": 201}
    )
    prompt_enhancer: bool = Field(
        True, description="Whether to refine prompt", json_schema_extra={"x-sr-order": 202}
    )
    negative_prompt: str = Field(
        None,
        description="The negative prompt you would like to use to generate images.",
        json_schema_extra={"x-sr-order": 203}
    )

    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        description=(
            "The same seed and the same prompt given to the same version of the model will output the same image every time."
        ),
        json_schema_extra={"x-sr-order": 401}
    )
    fast: bool = Field(
        True, description="Whether to use the fast model", json_schema_extra={"x-sr-order": 402}
    )
    number_of_images: int = Field(
        1,
        ge=1,
        le=4,
        multiple_of=1,
        description="Number of Images to generate.",
        json_schema_extra={"x-sr-order": 403}
    )
