import os
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import ImageToImageInput, HiDreamE1FullOutput
from .service_providers.replicate.adapter import ReplicateImageToImageAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="HiDream E1 Full API",
    description="API for HiDream E1 Full image-to-image model",
    version="1.0.0",
    output_schema=HiDreamE1FullOutput,
)

@service.app.post(
    f"/{model_path}/image-to-image",
    response_model=SubmitResponse,
    description="Generate image from input image and text prompts using HiDream E1 Full model",
)
def image_to_image(body: ImageToImageInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/image-to-image": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateImageToImageAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
}
