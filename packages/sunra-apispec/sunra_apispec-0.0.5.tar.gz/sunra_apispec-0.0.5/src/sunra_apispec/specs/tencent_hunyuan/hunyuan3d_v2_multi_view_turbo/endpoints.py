import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import ModelOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import ImageTo3DInput
from .service_providers.fal.adapter import (
    FalImageTo3DAdapter,
)


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Hunyuan3D V2 Multi-View Turbo API",
    description="API for Hunyuan3D V2 Multi-View Turbo 3D generation model",
    version="1.0.0",
    output_schema=ModelOutput,
)


@service.app.post(
    f"/{model_path}/image-to-3d",
    response_model=SubmitResponse,
    description="Generate 3D model from multi-view images",
)
def image_to_3d(body: ImageTo3DInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/image-to-3d": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalImageTo3DAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
} 