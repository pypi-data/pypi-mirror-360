import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import ImageToVideoInput, Seedance10LiteI2VOutput, StartEndImageToVideoInput
from .service_providers.volcengine.adapter import (
    VolcengineImageToVideoAdapter,
    VolcengineStartEndImageToVideoAdapter
)


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Doubao Seedance 1.0 Lite I2V API",
    description="API for Doubao Seedance 1.0 Lite image-to-video generation model",
    version="1.0.0",
    output_schema=Seedance10LiteI2VOutput,
)

@service.app.post(
    f"/{model_path}/image-to-video",
    response_model=SubmitResponse,
    description="Generate video from image and text prompt",
)
def image_to_video(body: ImageToVideoInput) -> SubmitResponse:
    pass


@service.app.post(
    f"/{model_path}/start-end-image-to-video",
    response_model=SubmitResponse,
    description="Generate video from start and end image and text prompt",
)
def start_end_image_to_video(body: StartEndImageToVideoInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/image-to-video": [
        {
            "service_provider": ServiceProviderEnum.VOLCENGINE.value,
            "adapter": VolcengineImageToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/start-end-image-to-video": [
        {
            "service_provider": ServiceProviderEnum.VOLCENGINE.value,
            "adapter": VolcengineStartEndImageToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
} 
