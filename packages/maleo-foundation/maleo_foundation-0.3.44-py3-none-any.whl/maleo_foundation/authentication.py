from pydantic import BaseModel, ConfigDict, Field, field_serializer
from starlette.authentication import AuthCredentials, BaseUser
from typing import Optional, Sequence
from maleo_foundation.enums import BaseEnums
from maleo_foundation.models.transfers.general.token import MaleoFoundationTokenGeneralTransfers

class Token(BaseModel):
    type: BaseEnums.TokenType = Field(..., description="Token's type")
    payload: MaleoFoundationTokenGeneralTransfers.DecodePayload = Field(..., description="Token's payload")

class Credentials(AuthCredentials):
    def __init__(
        self,
        token: Optional[Token] = None,
        scopes: Optional[Sequence[str]] = None
    ) -> None:
        self._token = token
        super().__init__(scopes)

    @property
    def token(self) -> Optional[Token]:
        return self._token

class User(BaseUser):
    def __init__(
        self,
        authenticated: bool = True,
        username: str = "",
        email: str = ""
    ) -> None:
        self._authenticated = authenticated
        self._username = username
        self._email = email

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def display_name(self) -> str:
        return self._username

    @property
    def identity(self) -> str:
        return self._email

class Authentication(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    credentials: Credentials = Field(..., description="Credentials's information")
    user: User = Field(..., description="User's information")

    @field_serializer('credentials')
    def serialize_credentials(self, credentials: Credentials, _info):
        return {
            "token": credentials.token.model_dump() if credentials.token is not None else None,
            "scopes": credentials.scopes if credentials.scopes is not None else None
        }

    @field_serializer('user')
    def serialize_user(self, user: User, _info):
        return {
            "is_authenticated": user.is_authenticated,
            "display_name": user.display_name,
            "identity": user.identity
        }
