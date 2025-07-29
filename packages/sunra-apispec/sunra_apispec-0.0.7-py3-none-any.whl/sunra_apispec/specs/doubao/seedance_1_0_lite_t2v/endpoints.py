import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import TextToVideoInput, Seedance10LiteT2VOutput
from .service_providers.volcengine.adapter import VolcengineTextToVideoAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Doubao Seedance 1.0 Lite T2V API",
    description="API for Doubao Seedance 1.0 Lite text-to-video generation model",
    version="1.0.0",
    output_schema=Seedance10LiteT2VOutput,
)

@service.app.post(
    f"/{model_path}/text-to-video",
    response_model=SubmitResponse,
    description="Generate video from text prompt",
)
def text_to_video(body: TextToVideoInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/text-to-video": [
        {
            "service_provider": ServiceProviderEnum.VOLCENGINE.value,
            "adapter": VolcengineTextToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
} 
