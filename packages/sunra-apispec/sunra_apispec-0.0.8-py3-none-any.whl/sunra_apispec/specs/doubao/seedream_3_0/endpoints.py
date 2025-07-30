import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import ImagesOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import TextToImageInput
from .service_providers.volcengine.adapter import VolcengineTextToImageAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Doubao Seedream 3.0 API",
    description="API for Doubao Seedream 3.0 text-to-image generation model",
    version="1.0.0",
    output_schema=ImagesOutput,
)

@service.app.post(
    f"/{model_path}/text-to-image",
    response_model=SubmitResponse,
    description="Generate image from text prompt",
)
def text_to_image(body: TextToImageInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/text-to-image": [
        {
            "service_provider": ServiceProviderEnum.VOLCENGINE.value,
            "adapter": VolcengineTextToImageAdapter,
            "request_type": RequestType.SYNC,
        }
    ],
}
