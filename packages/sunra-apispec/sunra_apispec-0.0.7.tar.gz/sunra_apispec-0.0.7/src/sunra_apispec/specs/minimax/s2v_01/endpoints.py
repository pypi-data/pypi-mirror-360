import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import VideoOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import SubjectReferenceInput
from .service_providers.minimax_official.adapter import MinimaxSubjectReferenceVideoAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Minimax S2V-01 API",
    description="API for Minimax S2V-01 video generation model",
    version="1.0.0",
    output_schema=VideoOutput,
)

@service.app.post(
    f"/{model_path}/image-to-video",
    response_model=SubmitResponse,
    description="Generate video from subject reference image and text prompt",
)
def subject_reference_to_video(body: SubjectReferenceInput) -> SubmitResponse:
    pass


registry_items = {
    f"{model_path}/image-to-video": [
        {
            "service_provider": ServiceProviderEnum.MINIMAX.value,
            "adapter": MinimaxSubjectReferenceVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
}
