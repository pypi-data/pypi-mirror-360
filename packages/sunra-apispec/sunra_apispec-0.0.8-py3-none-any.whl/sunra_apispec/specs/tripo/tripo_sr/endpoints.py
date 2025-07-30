import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.base.common import RequestType
from .sunra_schema import ImageTo3DInput, TripoSRModelOutput
from .service_providers.replicate.adapter import ReplicateImageTo3DAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="TripoSR API",
    description="API for the TripoSR 3D model generation service.",
    version="1.0.0",
    output_schema=TripoSRModelOutput,
)

@service.app.post(
    f"/{model_path}/image-to-3d",
    response_model=SubmitResponse,
    description="Generates 3D model from image",
)
def image_to_3D(body: ImageTo3DInput) -> SubmitResponse:
    pass 


registry_items = {
    f"{model_path}/image-to-3d": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateImageTo3DAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
}
