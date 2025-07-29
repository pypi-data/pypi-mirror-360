import os
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import ImagesOutput
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import TextToImageInput, ImageBlendingInput, FaceSwapInput, ImageEditingInput
from .service_providers.littercoder.adapter import (
    LittercoderTextToImageAdapter,
    LittercoderImageBlendingAdapter,
    LittercoderFaceSwapAdapter,
    LittercoderImageEditingAdapter
)


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Image S1 API",
    description="API for Sunra Image S1 model",
    version="1.0.0",
    output_schema=ImagesOutput,
)


@service.app.post(
    f"/{model_path}/text-to-image",
    response_model=SubmitResponse,
    description="Generate image from text prompts",
)
def text_to_image(body: TextToImageInput) -> SubmitResponse:
    pass


@service.app.post(
    f"/{model_path}/image-blending",
    response_model=SubmitResponse,
    description="Blend multiple images together",
)
def image_blending(body: ImageBlendingInput) -> SubmitResponse:
    pass


@service.app.post(
    f"/{model_path}/face-swap",
    response_model=SubmitResponse,
    description="Swap faces between two images",
)
def face_swap(body: FaceSwapInput) -> SubmitResponse:
    pass


@service.app.post(
    f"/{model_path}/image-editing",
    response_model=SubmitResponse,
    description="Edit images with text prompts",
)
def image_editing(body: ImageEditingInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/text-to-image": [
        {
            "service_provider": ServiceProviderEnum.LITTERCODER.value,
            "adapter": LittercoderTextToImageAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/image-blending": [
        {
            "service_provider": ServiceProviderEnum.LITTERCODER.value,
            "adapter": LittercoderImageBlendingAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/face-swap": [
        {
            "service_provider": ServiceProviderEnum.LITTERCODER.value,
            "adapter": LittercoderFaceSwapAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/image-editing": [
        {
            "service_provider": ServiceProviderEnum.LITTERCODER.value,
            "adapter": LittercoderImageEditingAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
}
