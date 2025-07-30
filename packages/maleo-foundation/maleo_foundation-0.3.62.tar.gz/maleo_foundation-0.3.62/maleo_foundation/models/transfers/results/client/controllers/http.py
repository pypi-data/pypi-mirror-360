from __future__ import annotations
from httpx import Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Any, Self
from maleo_foundation.types import BaseTypes


class BaseClientHTTPControllerResults(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    response: Response = Field(..., description="Client's HTTP Controller response")

    @model_validator(mode="after")
    def verify_response(self) -> Self:
        """Verify that the response is an instance of httpx.Response."""
        if not isinstance(self.response, Response):
            raise TypeError("Response must be an instance of httpx.Response")
        return self

    @property
    def status_code(self) -> int:
        """Get the status code of the response."""
        return self.response.status_code

    @property
    def success(self) -> bool:
        """Get the success status of the response."""
        return self.response.is_success

    @property
    def content(self) -> Any:
        """Get the content of the response."""
        # * Determine content type and parse accordingly
        content_type: str = self.response.headers.get("content-type", "")
        content_type = content_type.lower()
        if "application/json" in content_type:
            content = self.response.json()
        elif "text/" in content_type or "application/xml" in content_type:
            content = self.response.text
        else:
            content = self.response.content  # * Raw bytes for unknown types
        return content

    @property
    def json_content(self) -> BaseTypes.StringToAnyDict:
        # * Determine content type and parse accordingly
        content_type: str = self.response.headers.get("content-type", "")
        content_type = content_type.lower()
        if content_type != "application/json":
            raise ValueError("Response 'Content-Type' is not 'application/json'")
        return self.response.json()
