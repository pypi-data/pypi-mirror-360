import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import (
    TextToMusicInput, 
    AudioToAudioInput, 
    AudioInpaintInput, 
    AudioOutpaintInput,
    AceStepV135BOutput
)
from .service_providers.fal.adapter import (
    AceStepTextToMusicAdapter,
    AceStepMusicEditingAdapter,
    AceStepMusicExtendingAdapter,
    AceStepMusicInpaintingAdapter
)

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="ACE-STEP v1-3.5b API",
    description="API for ACE-STEP v1-3.5b model",
    version="1.0.0",
    output_schema=AceStepV135BOutput,
)

@service.app.post(
    f"/{model_path}/text-to-music",
    response_model=SubmitResponse,
    description="Generate music from text prompt using ACE-STEP v1-3.5b model.",
)
def text_to_music(body: TextToMusicInput) -> SubmitResponse:
    pass


@service.app.post(
    f"/{model_path}/music-editing",
    response_model=SubmitResponse,
    description="Edit music using ACE-STEP v1-3.5b model.",
)
def music_editing(body: AudioToAudioInput) -> SubmitResponse:
    pass


@service.app.post(
    f"/{model_path}/music-extending",
    response_model=SubmitResponse,
    description="Extend music using ACE-STEP v1-3.5b model.",
)
def music_extending(body: AudioOutpaintInput) -> SubmitResponse:
    pass


@service.app.post(
    f"/{model_path}/music-inpainting",
    response_model=SubmitResponse,
    description="Inpaint music using ACE-STEP v1-3.5b model.",
)
def music_inpainting(body: AudioInpaintInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/text-to-music": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": AceStepTextToMusicAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/music-editing": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": AceStepMusicEditingAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/music-extending": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": AceStepMusicExtendingAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/music-inpainting": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": AceStepMusicInpaintingAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
}
