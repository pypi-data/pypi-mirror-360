from __future__ import annotations

from typing import Any, Dict, Type
from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

class QueueStatus(BaseModel):
    status: str
    response_url: str
    status_url: str
    cancel_url: str
    logs: Dict[str, Any]
    metrics: Dict[str, Any]


class SubmitResponse(BaseModel):
    request_id: str
    response_url: str
    status_url: str
    cancel_url: str


class BaseAPIService():
    """Base class for API services with common queue-based endpoints"""
    
    def __init__(
        self, 
        title: str,
        description: str,
        version: str,
        output_schema: Type[BaseModel],
    ):
        """
        Initialize base API service
        
        Args:
            app: FastAPI application
            output_schema: Schema for model output (e.g. VideoOutput, ImagesOutput)
        """
        security = HTTPBearer(auto_error=True)
        self.app = FastAPI(
            title=title,
            description=description,
            version=version,
            servers=[{"url": "https://api.sunra.ai/v1/queue"}],
            dependencies=[Depends(security)],
        )
        self.app.openapi_version = "3.0.0"

        self.output_schema = output_schema
        self._setup_routes()
        
    def _setup_routes(self):
        """Set up common routes for queue-based API"""

        # Status endpoint
        @self.app.get(
            "/requests/{request_id}/status",
            response_model=QueueStatus,
            summary="Get request status",
            description="Check the status of a request"
        )
        def get_request_status(request_id: str) -> QueueStatus:
            pass

        # Cancel endpoint
        @self.app.post(
            "/requests/{request_id}/cancel",
            summary="Cancel request",
            description="Cancel a request that is in queue or in progress"
        )
        def cancel_request(request_id: str):
            pass
        
        # Get result endpoint
        @self.app.get(
            "/requests/{request_id}",
            response_model=self.output_schema,
            summary="Get request result",
            description="Get the result of a completed request"
        )
        def get_request_result(request_id: str) -> self.output_schema:
            pass


    def get_openapi(self):
        return self.app.openapi()
