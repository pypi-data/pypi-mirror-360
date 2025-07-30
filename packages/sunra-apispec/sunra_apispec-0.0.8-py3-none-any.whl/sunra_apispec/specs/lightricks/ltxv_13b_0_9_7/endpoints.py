import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from .sunra_schema import TextToVideoInput, ImageToVideoInput, LtxvVideoOutput
from .service_providers.replicate.adapter import (
    ReplicateTextToVideoAdapter, ReplicateImageToVideoAdapter
)


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Lightricks LTX Video 0.9.7 API",
    description="API for Lightricks LTX Video 0.9.7 model - A high-quality video generation model capable of creating videos from text prompts and images with advanced control over resolution, aspect ratio, frame count and frame rate.",
    version="1.0.0",
    output_schema=LtxvVideoOutput,
)

@service.app.post(
    f"/{model_path}/text-to-video",
    response_model=SubmitResponse,
    description="Generate videos from text prompts",
)
def text_to_video(body: TextToVideoInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/image-to-video",
    response_model=SubmitResponse,
    description="Generate videos from images and text prompts",
)
def image_to_video(body: ImageToVideoInput) -> SubmitResponse:
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
    f"{model_path}/image-to-video": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateImageToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
}
