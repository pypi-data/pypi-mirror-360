import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import ImagesOutput
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from .sunra_schema import TextToImageInput, ImageEditingInput
from .service_providers.openai_official.adapter import (
    OpenAITextToImageAdapter, OpenAIImageEditingAdapter,
)


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="OpenAI GPT Image 1 API",
    description="API for OpenAI GPT Image 1 model - A high-quality image generation and editing model capable of creating and editing images from text prompts with advanced features like transparency control and multiple output formats.",
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
    f"/{model_path}/image-editing",
    response_model=SubmitResponse,
    description="Edit images using text prompts and optional masks",
)
def image_editing(body: ImageEditingInput) -> SubmitResponse:
    pass

# Register adapters for service providers
registry_items = {
    f"{model_path}/text-to-image": [
        {
            "service_provider": ServiceProviderEnum.OPENAI.value,
            "adapter": OpenAITextToImageAdapter,
            "request_type": RequestType.SYNC,
        }
    ],
    f"{model_path}/image-editing": [
        {
            "service_provider": ServiceProviderEnum.OPENAI.value,
            "adapter": OpenAIImageEditingAdapter,
            "request_type": RequestType.SYNC,
        }
    ],
}
