from __future__ import annotations
from pydantic import model_validator
from maleo_foundation.models.schemas.result import BaseResultSchemas

class BaseClientServiceResultsTransfers:
    class Fail(BaseResultSchemas.Fail): pass

    class NotFound(BaseResultSchemas.NotFound): pass

    class NoData(BaseResultSchemas.NoData): pass

    class SingleData(BaseResultSchemas.SingleData): pass

    class UnpaginatedMultipleData(BaseResultSchemas.UnpaginatedMultipleData): pass

    class PaginatedMultipleData(BaseResultSchemas.PaginatedMultipleData):
        @model_validator(mode="before")
        @classmethod
        def calculate_pagination_component(cls, values: dict) -> dict:
            """Extracts pagination components (page, limit, total_data) before validation."""
            pagination = values.get("pagination")
            if pagination is None:
                raise ValueError("Pagination field did not exists")
            pagination = BaseResultSchemas.ExtendedPagination.model_validate(pagination)
            values["page"] = pagination.page
            values["limit"] = pagination.limit
            values["total_data"] = pagination.total_data

            return values