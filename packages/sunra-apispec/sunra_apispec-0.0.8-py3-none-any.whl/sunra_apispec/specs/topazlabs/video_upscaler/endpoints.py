import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.base.common import RequestType
from .sunra_schema import VideoUpscalerInput, VideoUpscalerOutput
from .service_providers.replicate.adapter import VideoUpscalerAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Topazlabs Video Upscaler API",
    description="An API service for enhancing and upscaling videos using the Topazlabs/Video-Upscaler model on Replicate.",
    version="1.0.0",
    output_schema=VideoUpscalerOutput,
)

@service.app.post(
    f"/{model_path}/video-upscale",
    response_model=SubmitResponse,
    description="Enhances and upscales an input video based on specified parameters.",
)
def video_upscaler(body: VideoUpscalerInput) -> SubmitResponse:
    pass 


registry_items = {
    f"{model_path}/video-upscale": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": VideoUpscalerAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
}
