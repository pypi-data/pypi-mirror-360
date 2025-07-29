import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import TextToSpeechInput, TurboV25Output
from .service_providers.elevenlabs_official.adapter import ElevenLabsTurboV25Adapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="ElevenLabs Turbo V2.5 API",
    description="API for ElevenLabs Turbo V2.5 text-to-speech generation",
    version="2.5",
    output_schema=TurboV25Output,
)

@service.app.post(
    f"/{model_path}/text-to-speech",
    response_model=SubmitResponse,
    description="Convert text into speech using ElevenLabs Turbo V2.5 model",
)
def text_to_speech(body: TextToSpeechInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/text-to-speech": [
        {
            "service_provider": ServiceProviderEnum.ELEVENLABS.value,
            "adapter": ElevenLabsTurboV25Adapter,
            "request_type": RequestType.SYNC,
        }
    ]
} 
