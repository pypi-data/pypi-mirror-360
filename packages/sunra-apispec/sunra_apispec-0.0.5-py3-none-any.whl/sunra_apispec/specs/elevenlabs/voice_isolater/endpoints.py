import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import AudioIsolationInput, VoiceIsolaterOutput
from .service_providers.elevenlabs_official.adapter import ElevenLabsVoiceIsolaterAdapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="ElevenLabs Voice Isolater API",
    description="API for ElevenLabs Voice Isolater audio isolation",
    version="1.0",
    output_schema=VoiceIsolaterOutput,
)

@service.app.post(
    f"/{model_path}/audio-isolation",
    response_model=SubmitResponse,
    description="Remove background noise and isolate vocals from audio using ElevenLabs Voice Isolater",
)
def audio_isolation(body: AudioIsolationInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/audio-isolation": [
        {
            "service_provider": ServiceProviderEnum.ELEVENLABS.value,
            "adapter": ElevenLabsVoiceIsolaterAdapter,
            "request_type": RequestType.SYNC,
        }
    ]
}
