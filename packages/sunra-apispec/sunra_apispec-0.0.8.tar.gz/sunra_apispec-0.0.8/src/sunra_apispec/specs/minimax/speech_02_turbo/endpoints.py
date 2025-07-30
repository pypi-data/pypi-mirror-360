import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import TextToSpeechInput, MinimaxSpeech02TurboOutput
from .service_providers.replicate.adapter import MinimaxTextToAudioAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Minimax speech-02-turbo API",
    description="API for Minimax speech-02-turbo text-to-audio generation model",
    version="1.0.0",
    output_schema=MinimaxSpeech02TurboOutput,
)

@service.app.post(
    f"/{model_path}/text-to-speech",
    response_model=SubmitResponse,
    description="Generate audio from text prompt",
)
def text_to_speech(body: TextToSpeechInput) -> SubmitResponse:
    pass

registry_items = {
    f"{model_path}/text-to-speech": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": MinimaxTextToAudioAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
}
