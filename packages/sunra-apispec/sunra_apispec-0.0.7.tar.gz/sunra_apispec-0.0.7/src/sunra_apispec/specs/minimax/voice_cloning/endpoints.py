import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import VoiceCloningInput, VoiceCloningOutput
from .service_providers.replicate.adapter import MinimaxVoiceCloningAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Minimax Voice-Cloning API",
    description="API for Minimax Voice-Cloning voice generation model",
    version="1.0.0",
    output_schema=VoiceCloningOutput,
)

@service.app.post(
    f"/{model_path}/voice-cloning",
    response_model=SubmitResponse,
    description="Cloning voice from source voice",
)
def voice_cloning(body: VoiceCloningInput) -> SubmitResponse:
    pass

registry_items = {
    f"{model_path}/voice-cloning": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": MinimaxVoiceCloningAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
}
