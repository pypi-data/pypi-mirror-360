import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import AudioOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import TextToSpeechInput
from .service_providers.openai_official.adapter import OpenAITextToSpeechAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="OpenAI TTS API",
    description="API for OpenAI text-to-speech model",
    version="1.0.0",
    output_schema=AudioOutput,
)


@service.app.post(
    f"/{model_path}/text-to-speech",
    response_model=SubmitResponse,
    description="Generate speech from text",
)
def text_to_speech(body: TextToSpeechInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/text-to-speech": [
        {
            "service_provider": ServiceProviderEnum.OPENAI.value,
            "adapter": OpenAITextToSpeechAdapter,
            "request_type": RequestType.SYNC,
        }
    ],
} 