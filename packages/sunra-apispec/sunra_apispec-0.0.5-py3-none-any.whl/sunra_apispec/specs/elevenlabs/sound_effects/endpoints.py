import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import TextToSoundEffectsInput, SoundEffectsOutput
from .service_providers.elevenlabs_official.adapter import ElevenLabsSoundEffectsAdapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="ElevenLabs Sound Effects API",
    description="API for ElevenLabs Sound Effects text-to-sound-effects generation",
    version="1.0",
    output_schema=SoundEffectsOutput,
)

@service.app.post(
    f"/{model_path}/text-to-sound-effects",
    response_model=SubmitResponse,
    description="Generate sound effects from text using ElevenLabs Sound Effects model",
)
def text_to_sound_effects(body: TextToSoundEffectsInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/text-to-sound-effects": [
        {
            "service_provider": ServiceProviderEnum.ELEVENLABS.value,
            "adapter": ElevenLabsSoundEffectsAdapter,
            "request_type": RequestType.SYNC,
        }
    ]
} 