import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import ImageOutput
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from .sunra_schema import UpscaleInput
from .service_providers.fal.adapter import FalImageUpscaleAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Crisp Upscale API",
    description="This API provides access to the Crisp Upscale model, allowing you to enhance image resolution and quality through asynchronous processing.",
    version="1.0.0",
    output_schema=ImageOutput,
)

@service.app.post(
    f"/{model_path}/upscale-image",
    response_model=SubmitResponse,
    description="upscale image",
)
def upscale_image(body: UpscaleInput) -> SubmitResponse:
    pass

# Register adapters for service providers
registry_items = {
    f"{model_path}/upscale-image": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalImageUpscaleAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
} 
