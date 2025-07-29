import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import VideoOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import PikaffectsInput
from .service_providers.fal.adapter import FalPikaffectsAdapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Pika Pikaffects API",
    description="A state-of-the-art image-to-video effect generation model by Pika",
    version="1.5",
    output_schema=VideoOutput,
)

@service.app.post(
    f"/{model_path}/pikaffects",
    response_model=SubmitResponse,
    description="Generate videos with special effects from images",
)
def pikaffects(body: PikaffectsInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/pikaffects": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalPikaffectsAdapter,
            "request_type": RequestType.ASYNC,
        }   
    ]
}
