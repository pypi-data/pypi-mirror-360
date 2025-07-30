import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import ImagesOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import (
    TextToImageInput,
    EditInput,
    ReframeInput,
    RemixInput,
    ReplaceBackgroundInput,
)
from .service_providers.fal.adapter import (
    FalTextToImageAdapter,
    FalEditAdapter,
    FalReframeAdapter,
    FalRemixAdapter,
    FalReplaceBackgroundAdapter,
)



model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Ideogram V3 API",
    description="API for Ideogram V3 image generation and editing",
    version="1.0.0",
    output_schema=ImagesOutput,
)

@service.app.post(
    f"/{model_path}/text-to-image",
    response_model=SubmitResponse,
    description="Generate images from text prompts",
)
def text_to_image(body: TextToImageInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/edit",
    response_model=SubmitResponse,
    description="Edit images using text prompts and optional masks",
)
def edit(body: EditInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/reframe",
    response_model=SubmitResponse,
    description="Reframe images to different resolutions",
)
def reframe(body: ReframeInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/remix",
    response_model=SubmitResponse,
    description="Remix images with text prompts",
)
def remix(body: RemixInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/replace-background",
    response_model=SubmitResponse,
    description="Replace image backgrounds using text prompts",
)
def replace_background(body: ReplaceBackgroundInput) -> SubmitResponse:
    pass

registry_items = {
    f"{model_path}/text-to-image": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalTextToImageAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/edit": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalEditAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/reframe": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalReframeAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/remix": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalRemixAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/replace-background": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalReplaceBackgroundAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
}

