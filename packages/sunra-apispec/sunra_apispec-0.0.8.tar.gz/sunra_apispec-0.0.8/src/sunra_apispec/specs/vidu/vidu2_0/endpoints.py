import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import VideoOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import (
    ImageToVideoInput,
    ReferenceImagesToVideoInput,
)
from .service_providers.vidu_official.adapter import (
    ViduImageToVideoAdapter,
    ViduReferenceImagesToVideoAdapter,
)


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Vidu API",
    description="API for Vidu video generation model",
    version="1.0.0",
    output_schema=VideoOutput,
)


@service.app.post(
    f"/{model_path}/image-to-video",
    response_model=SubmitResponse,
    description="Generate videos from images",
)
def image_to_video(body: ImageToVideoInput) -> SubmitResponse:
    pass


@service.app.post(
    f"/{model_path}/reference-images-to-video",
    response_model=SubmitResponse,
    description="Generate videos from reference images",
)
def reference_to_video(body: ReferenceImagesToVideoInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/image-to-video": [
        {
            "service_provider": ServiceProviderEnum.VIDU.value,
            "adapter": ViduImageToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/reference-images-to-video": [
        {
            "service_provider": ServiceProviderEnum.VIDU.value,
            "adapter": ViduReferenceImagesToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
}
