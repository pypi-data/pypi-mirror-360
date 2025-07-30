from __future__ import annotations
from fastapi import status
from pydantic import BaseModel, Field, model_validator
from typing import Any, Dict, Optional, Type, Union
from maleo_foundation.models.schemas.result import BaseResultSchemas, ResultMetadata
from maleo_foundation.types import BaseTypes


class BaseResponses:
    # * ----- ----- ----- Base ----- ----- ----- *#
    class Base(BaseModel):
        success: bool = Field(..., description="Success status")
        code: BaseTypes.OptionalString = Field(None, description="Optional result code")
        message: BaseTypes.OptionalString = Field(None, description="Optional message")
        description: BaseTypes.OptionalString = Field(
            None, description="Optional description"
        )
        data: Any = Field(..., description="Data")
        metadata: Optional[ResultMetadata] = Field(
            None, description="Optional metadata"
        )
        other: BaseTypes.OptionalAny = Field(
            None, description="Optional other information"
        )

    # * ----- ----- ----- Intermediary ----- ----- ----- *#
    class Fail(Base):
        success: BaseTypes.LiteralFalse = Field(False, description="Success status")  # type: ignore
        code: str = "MAL-FAI-001"  # type: ignore
        message: str = "Fail result"  # type: ignore
        description: str = "Operation failed."  # type: ignore
        data: None = Field(None, description="No data")
        other: BaseTypes.OptionalAny = Field(
            "Please try again later or contact administrator.",
            description="Response's other information",
        )

    class Success(Base):
        success: BaseTypes.LiteralTrue = Field(True, description="Success status")  # type: ignore
        code: str = "MAL-SCS-001"  # type: ignore
        message: str = "Success result"  # type: ignore
        description: str = "Operation succeeded."  # type: ignore
        data: Any = Field(..., description="Data")

    # * ----- ----- ----- Derived ----- ----- ----- *#
    class BadRequest(Fail):
        code: str = "MAL-BDR-001"
        message: str = "Bad Request"
        description: str = "Bad/Unexpected parameters given in the request"

    class InvalidExpand(BadRequest):
        code: str = "MAL-INE-001"
        message: str = "Invalid expand"
        description: str = (
            "Invalid expand field(s) configuration are given. Check 'other' for more information."
        )

    class InvalidParameter(BadRequest):
        code: str = "MAL-IPR-001"
        message: str = "Invalid parameters"
        description: str = (
            "Invalid parameters and/or parameters combinations is given. Check 'other' for more information."
        )

    class InvalidSystemRole(BadRequest):
        code: str = "MAL-ISR-001"
        message: str = "Invalid system role"
        description: str = (
            "Invalid system role is detected in authorization token. Check 'other' for more information."
        )

    class Unauthorized(Fail):
        code: str = "MAL-ATH-001"
        message: str = "Unauthorized Request"
        description: str = "You are unauthorized to request this resource"

    class Forbidden(Fail):
        code: str = "MAL-ATH-002"
        message: str = "Forbidden Request"
        description: str = "You are forbidden from requesting this resource"

    class NotFound(Fail):
        code: str = "MAL-NTF-001"
        message: str = "Resource not found"
        description: str = "The requested resource can not be found."

    class MethodNotAllowed(Fail):
        code: str = "MAL-MTA-002"
        message: str = "Method Not Allowed"
        description: str = "Method not allowed for requesting this resource"

    class ValidationError(Fail):
        code: str = "MAL-VLD-001"
        message: str = "Validation Error"
        description: str = (
            "Request validation failed due to missing or invalid fields. Check other for more info."
        )

    class RateLimitExceeded(Fail):
        code: str = "MAL-RTL-001"
        message: str = "Rate Limit Exceeded"
        description: str = (
            "This resource is requested too many times. Please try again later."
        )

    class ServerError(Fail):
        code: str = "MAL-EXC-001"
        message: str = "Unexpected Server Error"
        description: str = "An unexpected error occurred while processing your request."

    class NotImplemented(Fail):
        code: str = "MAL-NIM-001"
        message: str = "Not Implemented"
        description: str = "This request is not yet implemented by the system."

    class Unavailable(Fail):
        code: str = "MAL-UNV-001"
        message: str = "Unavailable"
        description: str = "The service is unavailable to process the request."

    class NoData(Success):
        code: str = "MAL-NDT-001"
        message: str = "No data found"
        description: str = "No data found in the requested resource."
        data: None = Field(None, description="No data")

    class SingleData(Success):
        code: str = "MAL-SGD-001"
        message: str = "Single data found"
        description: str = "Requested data found in database."
        data: Any = Field(..., description="Fetched single data")

    class UnpaginatedMultipleData(Success):
        code: str = "MAL-MTD-001"
        message: str = "Multiple unpaginated data found"
        description: str = "Requested unpaginated data found in database."
        data: BaseTypes.ListOfAny = Field(..., description="Unpaginated multiple data")

    class PaginatedMultipleData(Success):
        code: str = "MAL-MTD-002"
        message: str = "Multiple paginated data found"
        description: str = "Requested paginated data found in database."
        total_data: int = Field(..., ge=0, description="Total data count")
        pagination: BaseResultSchemas.ExtendedPagination = Field(
            ..., description="Pagination metadata"
        )
        page: int = Field(
            1, ge=1, description="Page number, must be >= 1.", exclude=True
        )
        limit: int = Field(
            10,
            ge=1,
            le=100,
            description="Page size, must be 1 <= limit <= 100.",
            exclude=True,
        )
        total_data: int = Field(..., ge=0, description="Total data count", exclude=True)

        @model_validator(mode="before")
        @classmethod
        def calculate_pagination(cls, values: dict) -> dict:
            """Calculates pagination metadata before validation."""
            total_data = values.get("total_data", 0)
            data = values.get("data", [])

            # * Get pagination values from inherited SimplePagination
            page = values.get("page", 1)
            limit = values.get("limit", 10)

            # * Calculate total pages
            total_pages = (total_data // limit) + (1 if total_data % limit > 0 else 0)

            # * Assign computed pagination object before validation
            values["pagination"] = BaseResultSchemas.ExtendedPagination(
                page=page,
                limit=limit,
                data_count=len(data),
                total_data=total_data,
                total_pages=total_pages,
            )
            return values

    # * ----- ----- Responses Class ----- ----- *#
    other_responses: Dict[int, Dict[str, Union[str, Type[Fail]]]] = {
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request Response",
            "model": BadRequest,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized Response",
            "model": Unauthorized,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Forbidden Response",
            "model": Forbidden,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found Response",
            "model": NotFound,
        },
        status.HTTP_405_METHOD_NOT_ALLOWED: {
            "description": "Method Not Allowed Response",
            "model": MethodNotAllowed,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation Error Response",
            "model": ValidationError,
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Rate Limit Exceeded Response",
            "model": RateLimitExceeded,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error Response",
            "model": ServerError,
        },
        status.HTTP_501_NOT_IMPLEMENTED: {
            "description": "Not Implemented Response",
            "model": NotImplemented,
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Service Unavailable Response",
            "model": Unavailable,
        },
    }
