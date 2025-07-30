import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import ImagesOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import BackgroundReplaceInput
from .service_providers.fal.adapter import BackgroundReplaceAdapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="bria bria-replace-background API",
    description="API for bria/bria-replace-background model",
    version="1.0.0",
    output_schema=ImagesOutput,
)

@service.app.post(
    f"/{model_path}/image-to-image",
    response_model=SubmitResponse,
    description="remoreplacee background using bria/bria-replace-background model.",
)
def image_to_image(body: BackgroundReplaceInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/image-to-image": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": BackgroundReplaceAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
}
