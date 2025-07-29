import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import VideoOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import PikascenesInput
from .service_providers.fal.adapter import FalPikascenesAdapter

model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Pika Pikascenes API",
    description="A state-of-the-art multi-image to video generation model by Pika",
    version="2.2",
    output_schema=VideoOutput,
)

@service.app.post(
    f"/{model_path}/pikascenes",
    response_model=SubmitResponse,
    description="Generate videos from multiple images and prompts",
)
def pikascenes(body: PikascenesInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/pikascenes": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalPikascenesAdapter,
            "request_type": RequestType.ASYNC,
        }   
    ]
}
