from pydantic import BaseModel, Field
from typing import Optional


class FalImageTo3DInput(BaseModel):
    """Input schema for FAL Hunyuan3D V2.1 API."""
    
    input_image_url: str = Field(
        ...,
        description="URL of image to use while generating the 3D model"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="The same seed and the same prompt given to the same version of the model will output the same output every time"
    )
    
    num_inference_steps: int = Field(
        default=50,
        ge=1,
        le=50,
        description="Number of inference steps to perform"
    )
    
    guidance_scale: float = Field(
        default=7.5,
        ge=0.0,
        le=20.0,
        description="Guidance scale for the model"
    )
    
    octree_resolution: int = Field(
        default=256,
        ge=1,
        le=1024,
        description="Octree resolution for the model"
    )
    
    textured_mesh: bool = Field(
        default=False,
        description="If set true, textured mesh will be generated and the price charged would be 3 times that of white mesh"
    )


class FalFile(BaseModel):
    """File output schema from FAL."""
    
    url: str = Field(..., description="The URL where the file can be downloaded from")
    content_type: Optional[str] = Field(None, description="The mime type of the file")
    file_name: Optional[str] = Field(None, description="The name of the file")
    file_size: Optional[int] = Field(None, description="The size of the file in bytes")


class FalImageTo3DOutput(BaseModel):
    """Output schema for FAL Hunyuan3D V2.1 API."""
    
    model_mesh: FalFile = Field(..., description="Generated 3D object file")
    model_glb: FalFile = Field(..., description="Generated 3D object file")
