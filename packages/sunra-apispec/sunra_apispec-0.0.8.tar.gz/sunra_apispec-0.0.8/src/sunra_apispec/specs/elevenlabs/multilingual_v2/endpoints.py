import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import TextToSpeechInput, MultilingualV2Output
from .service_providers.elevenlabs_official.adapter import ElevenLabsMultilingualV2Adapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="ElevenLabs Multilingual V2 API",
    description="API for ElevenLabs Multilingual V2 text-to-speech generation",
    version="2.0",
    output_schema=MultilingualV2Output,
)

@service.app.post(
    f"/{model_path}/text-to-speech",
    response_model=SubmitResponse,
    description="Convert text into audio using ElevenLabs Multilingual V2 model",
)
def text_to_speech(body: TextToSpeechInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/text-to-speech": [
        {
            "service_provider": ServiceProviderEnum.ELEVENLABS.value,
            "adapter": ElevenLabsMultilingualV2Adapter,
            "request_type": RequestType.SYNC,
        }
    ]
}
