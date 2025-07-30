import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import SpeechToTextInput, GPT4oTranscribeOutput
from .service_providers.openai_official.adapter import OpenAISpeechToTextAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="OpenAI Transcribe API",
    description="API for OpenAI speech-to-text model",
    version="1.0.0",
    output_schema=GPT4oTranscribeOutput,
)


@service.app.post(
    f"/{model_path}/speech-to-text",
    response_model=SubmitResponse,
    description="Transcribe speech to text",
)
def speech_to_text(body: SpeechToTextInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/speech-to-text": [
        {
            "service_provider": ServiceProviderEnum.OPENAI.value,
            "adapter": OpenAISpeechToTextAdapter,
            "request_type": RequestType.SYNC,
        }
    ],
}
