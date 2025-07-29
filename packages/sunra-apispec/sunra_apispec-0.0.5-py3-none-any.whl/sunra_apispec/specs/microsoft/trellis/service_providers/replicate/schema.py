from enum import Enum
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field


class Status(Enum):
    STARTING = "starting"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"
    FAILED = "failed"


class WebhookEvent(Enum):
    START = "start"
    OUTPUT = "output"
    LOGS = "logs"
    COMPLETED = "completed"


class ReplicateInput(BaseModel):
    images: List[str] = Field(
        ...,
        title="Images",
        description="List of input images to generate 3D asset from",
        json_schema_extra={"x-order": 0},
    )
    seed: Optional[int] = Field(
        0,
        title="Seed",
        description="Random seed for generation",
        json_schema_extra={"x-order": 1},
    )
    randomize_seed: Optional[bool] = Field(
        True, title="Randomize Seed", description="Randomize seed", json_schema_extra={"x-order": 2}
    )
    generate_color: Optional[bool] = Field(
        True, title="Generate Color", description="Generate color video render", json_schema_extra={"x-order": 3}
    )
    generate_normal: Optional[bool] = Field(
        False, title="Generate Normal", description="Generate normal video render", json_schema_extra={"x-order": 4}
    )
    generate_model: Optional[bool] = Field(
        False, title="Generate Model", description="Generate 3D model file (GLB)", json_schema_extra={"x-order": 5}
    )
    save_gaussian_ply: Optional[bool] = Field(
        False, title="Save Gaussian Ply", description="Save Gaussian point cloud as PLY file", json_schema_extra={"x-order": 6}
    )
    return_no_background: Optional[bool] = Field(
        False, title="Return No Background", description="Return the preprocessed images without background", json_schema_extra={"x-order": 7}
    )
    ss_guidance_strength: Optional[float] = Field(
        7.5,
        ge=0,
        le=10,
        title="Ss Guidance Strength",
        description="Stage 1: Sparse Structure Generation - Guidance Strength",
        json_schema_extra={"x-order": 8},
    )
    ss_sampling_steps: Optional[int] = Field(
        12,
        ge=1,
        le=50,
        title="Ss Sampling Steps",
        description="Stage 1: Sparse Structure Generation - Sampling Steps",
        json_schema_extra={"x-order": 9},
    )
    slat_guidance_strength: Optional[float] = Field(
        3,
        ge=0,
        le=10,
        title="Slat Guidance Strength",
        description="Stage 2: Structured Latent Generation - Guidance Strength",
        json_schema_extra={"x-order": 10},
    )
    slat_sampling_steps: Optional[int] = Field(
        12,
        ge=1,
        le=50,
        title="Slat Sampling Steps",
        description="Stage 2: Structured Latent Generation - Sampling Steps",
        json_schema_extra={"x-order": 11},
    )
    mesh_simplify: Optional[float] = Field(
        0.95,
        ge=0.9,
        le=0.98,
        title="Mesh Simplify",
        description="GLB Extraction - Mesh Simplification (only used if generate_model=True)",
        json_schema_extra={"x-order": 12},
    )
    texture_size: Optional[int] = Field(
        1024,
        ge=512,
        le=2048,
        title="Texture Size",
        description="GLB Extraction - Texture Size (only used if generate_model=True)",
        json_schema_extra={"x-order": 13},
    )


class ReplicateOutput(BaseModel):
    model_file: Optional[str] = Field(None, title="Model File", format="uri")
    color_video: Optional[str] = Field(None, title="Color Video", format="uri")
    gaussian_ply: Optional[str] = Field(None, title="Gaussian Ply", format="uri")
    normal_video: Optional[str] = Field(None, title="Normal Video", format="uri")
    combined_video: Optional[str] = Field(None, title="Combined Video", format="uri")
    no_background_images: Optional[List[str]] = Field(None, title="No Background Images")


class Output(ReplicateOutput):
    pass


class ValidationError(BaseModel):
    loc: List[Union[str, int]] = Field(..., title="Location")
    msg: str = Field(..., title="Message")
    type: str = Field(..., title="Error Type")


class PredictionRequest(BaseModel):
    input: Optional[ReplicateInput] = Field(None, title="Input")
    webhook: Optional[str] = Field(
        None, title="Webhook", maxLength=65536, minLength=1, format="uri"
    )
    webhook_events_filter: Optional[List[WebhookEvent]] = Field(
        ["start", "output", "logs", "completed"], title="Webhook Events Filter"
    )
    id: Optional[str] = Field(None, title="Id")
    created_at: Optional[str] = Field(None, title="Created At", format="date-time")
    output_file_prefix: Optional[str] = Field(None, title="Output File Prefix")


class PredictionResponse(BaseModel):
    id: Optional[str] = Field(None, title="Id")
    logs: Optional[str] = Field("", title="Logs")
    error: Optional[str] = Field(None, title="Error")
    input: Optional[ReplicateInput] = Field(None, title="Input")
    output: Optional[Output] = Field(None, title="Output")
    status: Optional[Status] = Field(None, title="Status")
    metrics: Optional[Dict[str, Any]] = Field(None, title="Metrics")
    version: Optional[str] = Field(None, title="Version")
    created_at: Optional[str] = Field(None, title="Created At", format="date-time")
    started_at: Optional[str] = Field(None, title="Started At", format="date-time")
    completed_at: Optional[str] = Field(None, title="Completed At", format="date-time")


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = Field(None, title="Detail")