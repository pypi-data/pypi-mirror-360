from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator
from typing import Any, Dict, Optional, Self, Union
from maleo_foundation.enums import BaseEnums
from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_foundation.types import BaseTypes


class FieldExpansionMetadata(BaseModel):
    success: bool = Field(..., description="Field expansion's success status")
    code: BaseTypes.OptionalString = Field(None, description="Optional result code")
    message: BaseTypes.OptionalString = Field(None, description="Optional message")
    description: BaseTypes.OptionalString = Field(
        None, description="Optional description"
    )
    other: BaseTypes.OptionalAny = Field(None, description="Optional other information")


class ResultMetadata(BaseModel):
    field_expansion: Optional[Union[str, Dict[str, FieldExpansionMetadata]]] = Field(
        None, description="Field expansion metadata"
    )


class BaseResultSchemas:
    class ExtendedPagination(BaseGeneralSchemas.SimplePagination):
        data_count: int = Field(..., description="Fetched data count")
        total_data: int = Field(..., description="Total data count")
        total_pages: int = Field(..., description="Total pages count")

    # * ----- ----- ----- Base ----- ----- ----- *#
    class Base(BaseModel):
        success: bool = Field(..., description="Success status")
        exception: Optional[BaseEnums.ExceptionType] = Field(
            None, description="Exception type (optional)"
        )
        timestamp: datetime = Field(datetime.now(timezone.utc), description="Timestamp")
        origin: BaseEnums.OperationOrigin = Field(..., description="Operation origin")
        layer: BaseEnums.OperationLayer = Field(..., description="Operation layer")
        target: Optional[BaseEnums.OperationTarget] = Field(
            None, description="Operation target (optional)"
        )
        environment: Optional[BaseEnums.EnvironmentType] = Field(
            None, description="Operation target environment (optional)"
        )
        resource: str = Field(..., description="Resource name")
        operation: BaseEnums.OperationType = Field(..., description="Operation type")
        create_type: Optional[BaseEnums.CreateType] = Field(
            None, description="Create type (optional)"
        )
        update_type: Optional[BaseEnums.UpdateType] = Field(
            None, description="Update type (optional)"
        )
        status_update_type: Optional[BaseEnums.StatusUpdateType] = Field(
            None, description="Status update type (optional)"
        )
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

        @model_validator(mode="after")
        def verify_fields(self) -> Self:
            """Verify that the required fields are set."""
            if self.origin is BaseEnums.OperationOrigin.SERVICE:
                if self.layer not in BaseEnums.ServiceOperationLayer:
                    raise ValueError(
                        f"Invalid layer '{self.layer}' for service operation."
                    )
                if self.target and self.target not in BaseEnums.ServiceOperationTarget:
                    raise ValueError(
                        f"Invalid target '{self.target}' for service operation."
                    )
            elif self.origin is BaseEnums.OperationOrigin.CLIENT:
                if self.layer not in BaseEnums.ClientOperationLayer:
                    raise ValueError(
                        f"Invalid layer '{self.layer}' for client operation."
                    )
                if self.target and self.target not in BaseEnums.ClientOperationTarget:
                    raise ValueError(
                        f"Invalid target '{self.target}' for client operation."
                    )
            else:
                raise ValueError(
                    f"Invalid operation origin '{self.origin}'. Must be 'service' or 'client'."
                )

            if self.operation is BaseEnums.OperationType.CREATE:
                if self.create_type is None:
                    raise ValueError("Create type must be set for create operations.")
            elif self.operation is BaseEnums.OperationType.UPDATE:
                if self.update_type is None:
                    raise ValueError("Update type must be set for update operations.")
                if self.update_type is BaseEnums.UpdateType.STATUS:
                    if self.status_update_type is None:
                        raise ValueError(
                            "Status update type must be set for status update operations."
                        )

            return self

    # * ----- ----- ----- Intermediary ----- ----- ----- *#
    class Fail(Base):
        success: BaseTypes.LiteralFalse = Field(False, description="Success status")  # type: ignore
        exception: BaseEnums.ExceptionType = Field(  # type: ignore
            ..., description="Exception type"
        )
        code: str = "MAL-FAI-001"  # type: ignore
        message: str = "Fail result"  # type: ignore
        description: str = "Operation failed."  # type: ignore
        data: None = Field(None, description="No data")

    class Success(Base):
        success: BaseTypes.LiteralTrue = Field(True, description="Success status")  # type: ignore
        code: str = "MAL-SCS-001"  # type: ignore
        message: str = "Success result"  # type: ignore
        description: str = "Operation succeeded."  # type: ignore
        data: Any = Field(..., description="Data")

    # * ----- ----- ----- Derived ----- ----- ----- *#
    class NotFound(Fail):
        code: str = "MAL-NTF-001"
        exception: BaseEnums.ExceptionType = Field(
            BaseEnums.ExceptionType.NOT_FOUND, description="Exception type"
        )
        message: str = "Resource not found"
        description: str = "The requested resource can not be found."

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

    class PaginatedMultipleData(
        UnpaginatedMultipleData, BaseGeneralSchemas.SimplePagination
    ):
        code: str = "MAL-MTD-002"
        message: str = "Multiple paginated data found"
        description: str = "Requested paginated data found in database."
        total_data: int = Field(..., ge=0, description="Total data count")
        pagination: "BaseResultSchemas.ExtendedPagination" = Field(
            ..., description="Pagination metadata"
        )


BaseResultSchemas.PaginatedMultipleData.model_rebuild()
