from __future__ import annotations
from fastapi import status, Response
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from maleo_foundation.enums import BaseEnums


class BaseServiceRESTControllerResults(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = Field(..., description="REST Controller's success status")
    response_type: BaseEnums.RESTControllerResponseType = Field(
        BaseEnums.RESTControllerResponseType.JSON,
        description="REST Controller's response class",
    )
    content: Any = Field(..., description="REST Controller's response content")
    status_code: int = Field(
        status.HTTP_200_OK, description="REST Controller's response status code"
    )

    @property
    def response(self) -> Response:
        response_cls = self.response_type.get_response_type()
        return response_cls(content=self.content, status_code=self.status_code)
