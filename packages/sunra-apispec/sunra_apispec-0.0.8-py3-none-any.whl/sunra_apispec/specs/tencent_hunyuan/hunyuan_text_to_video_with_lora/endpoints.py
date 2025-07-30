import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from .sunra_schema import TextToVideoInput, HunyuanVideoLoraOutput
from .service_providers.replicate.adapter import ReplicateTextToVideoAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Tencent Hunyuan Video LoRA API",
    description="API for Tencent Hunyuan Video with LoRA support - A high-quality video generation model capable of creating videos from text prompts with custom LoRA models for style and concept control.",
    version="1.0.0",
    output_schema=HunyuanVideoLoraOutput,
)

@service.app.post(
    f"/{model_path}/text-to-video",
    response_model=SubmitResponse,
    description="Generate videos from text prompts with LoRA support",
)
def text_to_video(body: TextToVideoInput) -> SubmitResponse:
    pass

# Register adapters for service providers
registry_items = {
    f"{model_path}/text-to-video": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateTextToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
}
