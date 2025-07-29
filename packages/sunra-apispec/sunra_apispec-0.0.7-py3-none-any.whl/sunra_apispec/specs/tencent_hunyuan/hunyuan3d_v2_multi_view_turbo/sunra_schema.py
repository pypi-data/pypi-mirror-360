from pydantic import BaseModel, Field, HttpUrl


class ImageTo3DInput(BaseModel):
    """Input schema for Hunyuan3D V2 Multi-View Turbo image-to-3D generation."""
    
    front_image: HttpUrl | str = Field(
        ...,
        description="URL of front image to use while generating the 3D model",
        json_schema_extra={"x-sr-order": 301}
    )
    
    back_image: HttpUrl | str = Field(
        ...,
        description="URL of back image to use while generating the 3D model",
        json_schema_extra={"x-sr-order": 302}
    )
    
    left_image: HttpUrl | str = Field(
        ...,
        description="URL of left image to use while generating the 3D model",
        json_schema_extra={"x-sr-order": 303}
    )
    
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        description="The same seed and the same prompt given to the same version of the model will output the same output every time",
        json_schema_extra={"x-sr-order": 310}
    )
    
    number_of_steps: int = Field(
        default=50,
        ge=1,
        le=50,
        multiple_of=1,
        description="Number of inference steps to perform",
        json_schema_extra={"x-sr-order": 311}
    )
    
    guidance_scale: float = Field(
        default=7.5,
        ge=0.0,
        le=20.0,
        multiple_of=0.1,
        description="Guidance scale for the model",
        json_schema_extra={"x-sr-order": 312}
    )
    
    octree_resolution: int = Field(
        default=256,
        ge=1,
        le=1024,
        multiple_of=1,
        description="Octree resolution for the model",
        json_schema_extra={"x-sr-order": 401}
    )
    
    shape_only: bool = Field(
        default=True,
        description="If set false, textured mesh will be generated and the price charged would be 3 times that of shape only",
        json_schema_extra={"x-sr-order": 402}
    ) 