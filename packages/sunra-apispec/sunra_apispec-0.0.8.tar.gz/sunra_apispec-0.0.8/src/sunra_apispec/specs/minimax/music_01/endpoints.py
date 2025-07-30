import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import AudioOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import TextToMusicInput
from .service_providers.replicate.adapter import MinimaxTextToMusicAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Minimax Music-01 API",
    description="API for Minimax Music-01 music generation model",
    version="1.0.0",
    output_schema=AudioOutput,
)

@service.app.post(
    f"/{model_path}/text-to-music",
    response_model=SubmitResponse,
    description="Generate music from text prompt and optional audio references",
)
def text_to_music(body: TextToMusicInput) -> SubmitResponse:
    pass

registry_items = {
    f"{model_path}/text-to-music": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": MinimaxTextToMusicAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
}
