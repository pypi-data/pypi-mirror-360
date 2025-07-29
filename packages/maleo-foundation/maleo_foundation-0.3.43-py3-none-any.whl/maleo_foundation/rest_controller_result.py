from fastapi import status
from maleo_foundation.models.transfers.results.service.controllers.rest \
    import BaseServiceRESTControllerResults
from maleo_foundation.models.responses import BaseResponses

class RESTControllerResultsConstants:
    BAD_REQUEST = BaseServiceRESTControllerResults(
        success=False,
        content=BaseResponses.BadRequest().model_dump(),
        status_code=status.HTTP_400_BAD_REQUEST
    )

    INVALID_EXPAND = BaseServiceRESTControllerResults(
        success=False,
        content=BaseResponses.InvalidExpand().model_dump(),
        status_code=status.HTTP_400_BAD_REQUEST
    )

    UNAUTHORIZED = BaseServiceRESTControllerResults(
        success=False,
        content=BaseResponses.Unauthorized().model_dump(),
        status_code=status.HTTP_401_UNAUTHORIZED
    )

    FORBIDDEN = BaseServiceRESTControllerResults(
        success=False,
        content=BaseResponses.Forbidden().model_dump(),
        status_code=status.HTTP_403_FORBIDDEN
    )

    METHOD_NOT_ALLOWED = BaseServiceRESTControllerResults(
        success=False,
        content=BaseResponses.MethodNotAllowed().model_dump(),
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED
    )

    VALIDATION_ERROR = BaseServiceRESTControllerResults(
        success=False,
        content=BaseResponses.ValidationError().model_dump(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

    RATE_LIMIT_EXCEEDED = BaseServiceRESTControllerResults(
        success=False,
        content=BaseResponses.RateLimitExceeded().model_dump(),
        status_code=status.HTTP_429_TOO_MANY_REQUESTS
    )

    SERVER_ERROR = BaseServiceRESTControllerResults(
        success=False,
        content=BaseResponses.ServerError().model_dump(),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    NOT_IMPLEMENTED = BaseServiceRESTControllerResults(
        success=False,
        content=BaseResponses.NotImplemented().model_dump(),
        status_code=status.HTTP_501_NOT_IMPLEMENTED
    )