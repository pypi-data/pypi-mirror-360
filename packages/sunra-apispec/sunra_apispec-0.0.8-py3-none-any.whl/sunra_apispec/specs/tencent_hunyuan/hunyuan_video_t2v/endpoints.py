import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import TextToVideoInput, HunyuanVideoT2VOutput
from .service_providers.replicate.adapter import ReplicateTextToVideoAdapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Tencent Hunyuan Video Generation API",
    description="A state-of-the-art text-to-video generation model from Tencent",
    version="1.0.0",
    output_schema=HunyuanVideoT2VOutput,
)

@service.app.post(
    f"/{model_path}/text-to-video",
    response_model=SubmitResponse,
    description="Generate videos from text descriptions",
)
def text_to_video(body: TextToVideoInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/text-to-video": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateTextToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
}
