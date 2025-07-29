import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import VideoOutput
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from .sunra_schema import TextLipSyncInput, AudioLipSyncInput
from .service_providers.replicate.adapter import ReplicateTextToVideoAdapter, ReplicateAudioToVideoAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Kling Lip Sync API",
    description="API for Kling Lip Sync generation model - Add lip-sync to any video with an audio file or text.",
    version="1.0.0",
    output_schema=VideoOutput,
)

@service.app.post(
    f"/{model_path}/text-lip-sync",
    response_model=SubmitResponse,
    description="Add lip-sync to any video with text input",
)
def text_lip_sync(body: TextLipSyncInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/audio-lip-sync",
    response_model=SubmitResponse,
    description="Add lip-sync to any video with audio input",
)
def audio_lip_sync(body: AudioLipSyncInput) -> SubmitResponse:
    pass 

registry_items = {
    f"{model_path}/text-lip-sync": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateTextToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/audio-lip-sync": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateAudioToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
} 
