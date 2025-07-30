# Schema for Image-to-3D generation with Trellis

from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from sunra_apispec.base.output_schema import SunraFile

class ImageTo3DInput(BaseModel):
    images: List[HttpUrl | str] = Field(
        ...,
        title="Images",
        description="List of input images to generate 3D asset from",
        json_schema_extra={"x-sr-order": 201},
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        description="Random seed for generation",
        json_schema_extra={"x-sr-order": 202},
    )
    generate_color: bool = Field(
        False, title="Generate Color", description="Generate color video render", json_schema_extra={"x-sr-order": 401}
    )
    generate_normal: bool = Field(
        False, title="Generate Normal", description="Generate normal video render", json_schema_extra={"x-sr-order": 402}
    )
    generate_model: bool = Field(
        True, title="Generate Model", description="Generate 3D model file (GLB)", json_schema_extra={"x-sr-order": 403}
    )
    generate_point_cloud: bool = Field(
        False, title="Save Gaussian Ply", description="Save Gaussian point cloud as PLY file", json_schema_extra={"x-sr-order": 404}
    )
    generate_background_removed_images: bool = Field(
        False, title="Return No Background", description="Return the preprocessed images without background", json_schema_extra={"x-sr-order": 405}
    )
    ss_guidance_strength: float = Field(
        7.5,
        ge=0,
        le=10,
        multiple_of=0.01,
        title="Ss Guidance Strength",
        description="Stage 1: Sparse Structure Generation - Guidance Strength",
        json_schema_extra={"x-sr-order": 406},
    )
    ss_sampling_steps: int = Field(
        12,
        ge=1,
        le=50,
        multiple_of=1,
        title="Ss Sampling Steps",
        description="Stage 1: Sparse Structure Generation - Sampling Steps",
        json_schema_extra={"x-sr-order": 407},
    )
    slat_guidance_strength: float = Field(
        3,
        ge=0,
        le=10,
        multiple_of=0.01,
        title="Slat Guidance Strength",
        description="Stage 2: Structured Latent Generation - Guidance Strength",
        json_schema_extra={"x-sr-order": 408},
    )
    slat_sampling_steps: int = Field(
        12,
        ge=1,
        le=50,
        multiple_of=1,
        title="Slat Sampling Steps",
        description="Stage 2: Structured Latent Generation - Sampling Steps",
        json_schema_extra={"x-sr-order": 409},
    )
    mesh_simplify: float = Field(
        0.9,
        ge=0.9,
        le=0.98,
        multiple_of=0.01,
        title="Mesh Simplify",
        description="GLB Extraction - Mesh Simplification (only used if generate_model=True)",
        json_schema_extra={"x-sr-order": 410},
    )
    texture_size: int = Field(
        2048,
        ge=512,
        le=2048,
        multiple_of=1,
        title="Texture Size",
        description="GLB Extraction - Texture Size (only used if generate_model=True)",
        json_schema_extra={"x-sr-order": 411},
    )
    

class TrellisModelOutput(BaseModel):
    model_mesh: Optional[SunraFile] = None
    normal_video: Optional[SunraFile] = None
    color_video: Optional[SunraFile] = None
    model_ply: Optional[SunraFile] = None
    combined_video: Optional[SunraFile] = None
    background_removed_images: Optional[List[SunraFile]] = None
    
    predict_time: float = Field(
        ...,
        title="Predict Time",
        description="Time taken to generate the 3D model",
    )
