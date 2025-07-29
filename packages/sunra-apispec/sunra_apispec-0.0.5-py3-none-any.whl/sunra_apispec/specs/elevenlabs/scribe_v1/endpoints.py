import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import SpeechToTextInput, ScribeV1Output
from .service_providers.elevenlabs_official.adapter import ElevenLabsScribeV1Adapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="ElevenLabs Scribe V1 API",
    description="API for ElevenLabs Scribe V1 speech-to-text transcription",
    version="1.0",
    output_schema=ScribeV1Output,
)

@service.app.post(
    f"/{model_path}/speech-to-text",
    response_model=SubmitResponse,
    description="Transcribe speech to text using ElevenLabs Scribe V1 model",
)
def speech_to_text(body: SpeechToTextInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/speech-to-text": [
        {
            "service_provider": ServiceProviderEnum.ELEVENLABS.value,
            "adapter": ElevenLabsScribeV1Adapter,
            "request_type": RequestType.SYNC,
        }
    ]
}
