import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.base.common import RequestType
from .sunra_schema import ImageUpscalerInput, ImageUpscalerOutput
from .service_providers.replicate.adapter import ImageUpscalerAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Topazlabs Image Upscaler API",
    description="An API service for enhancing and upscaling images using the Topazlabs/Image-Upscaler model on Replicate.",
    version="1.0.0",
    output_schema=ImageUpscalerOutput,
)

@service.app.post(
    f"/{model_path}/image-upscale",
    response_model=SubmitResponse,
    description="Enhances and upscales an input image based on specified parameters.",
)
def image_upscaler(body: ImageUpscalerInput) -> SubmitResponse:
    pass 


registry_items = {
    f"{model_path}/image-upscale": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ImageUpscalerAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
}
