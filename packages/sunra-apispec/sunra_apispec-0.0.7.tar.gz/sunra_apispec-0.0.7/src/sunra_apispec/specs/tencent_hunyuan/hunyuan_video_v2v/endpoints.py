import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import VideoToVideoInput, HunyuanVideoV2VOutput
from .service_providers.fal.adapter import FalVideoToVideoAdapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Tencent Hunyuan Video Generation API",
    description="A state-of-the-art video-to-video generation model from Tencent",
    version="1.0.0",
    output_schema=HunyuanVideoV2VOutput,
)

@service.app.post(
    f"/{model_path}/video-to-video",
    response_model=SubmitResponse,
    description="Generate videos from videos",
)
def inpaint(body: VideoToVideoInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/video-to-video": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalVideoToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
}
