# Schema for Image-to-3D generation with TripoSR

from pydantic import BaseModel, Field, HttpUrl
from sunra_apispec.base.output_schema import ModelOutput


class ImageTo3DInput(BaseModel):
    image: HttpUrl | str = Field(
      ...,
      title="Image Path",
      description="Input Image",
      json_schema_extra={"x-sr-order": 201},
    )
    remove_background: bool = Field(
        True,
        title="Do Remove Background",
        json_schema_extra={"x-sr-order": 301},
    )
    foreground_ratio: float = Field(
        0.85,
        ge=0.5,
        le=1,
        multiple_of=0.01,
        title="Foreground Ratio",
        json_schema_extra={"x-sr-order": 302},
    )


class TripoSRModelOutput(ModelOutput):
    predict_time: float = Field(
        ...,
        title="Predict Time",
        description="Time taken to generate the 3D model",
    )
