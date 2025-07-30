import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import VideoOutput
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from .sunra_schema import ReferenceImagesToVideoInput, TextToVideoInput, ImageToVideoInput
from .service_providers.replicate.adapter import (
    ReplicateTextToVideoAdapter, 
    ReplicateImageToVideoAdapter, 
    ReplicateReferenceImagesToVideoAdapter
)
from .service_providers.kling_official.adapter import (
    KlingTextToVideoAdapter,
    KlingImageToVideoAdapter,
    KlingReferenceImagesToVideoAdapter
)


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Kling v1.6-pro API",
    description="API for Kling v1.6-pro text-to-video generation model - Generate 5s and 10s videos in 1080p resolution",
    version="1.0.0",
    output_schema=VideoOutput,
)

@service.app.post(
    f"/{model_path}/text-to-video",
    response_model=SubmitResponse,
    description="Generate video from text prompts",
)
def text_to_video(body: TextToVideoInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/image-to-video",
    response_model=SubmitResponse,
    description="Generate video from image",
)
def image_to_video(body: ImageToVideoInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/reference-images-to-video",
    response_model=SubmitResponse,
    description="Generate video from reference images",
)
def reference_images_to_video(body: ReferenceImagesToVideoInput) -> SubmitResponse:
    pass

registry_items = {
    f"{model_path}/text-to-video": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateTextToVideoAdapter,
            "request_type": RequestType.ASYNC,
        },
        {
            "service_provider": ServiceProviderEnum.KLING.value,
            "adapter": KlingTextToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/image-to-video": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateImageToVideoAdapter,
            "request_type": RequestType.ASYNC,
        },
        {
            "service_provider": ServiceProviderEnum.KLING.value,
            "adapter": KlingImageToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/reference-images-to-video": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateReferenceImagesToVideoAdapter,
            "request_type": RequestType.ASYNC,
        },
        {
            "service_provider": ServiceProviderEnum.KLING.value,
            "adapter": KlingReferenceImagesToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
}