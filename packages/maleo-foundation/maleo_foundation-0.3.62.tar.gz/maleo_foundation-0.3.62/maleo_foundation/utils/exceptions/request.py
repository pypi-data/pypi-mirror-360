from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from maleo_foundation.models.responses import BaseResponses


class BaseRequestExceptions:
    @staticmethod
    def authentication_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            content=BaseResponses.Unauthorized(other=str(exc)).model_dump(mode="json"),  # type: ignore
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        serialized_error = jsonable_encoder(exc.errors())
        return JSONResponse(
            content=BaseResponses.ValidationError(other=serialized_error).model_dump(mode="json"),  # type: ignore
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @staticmethod
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code in BaseResponses.other_responses:
            return JSONResponse(
                content=BaseResponses.other_responses[exc.status_code]["model"]().model_dump(mode="json"),  # type: ignore
                status_code=exc.status_code,
            )

        return JSONResponse(
            content=BaseResponses.ServerError().model_dump(mode="json"),  # type: ignore
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
