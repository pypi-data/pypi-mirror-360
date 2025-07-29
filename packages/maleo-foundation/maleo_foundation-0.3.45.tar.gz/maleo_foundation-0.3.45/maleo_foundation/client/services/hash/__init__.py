from __future__ import annotations
from pydantic import Field
from maleo_foundation.managers.client.base import ClientServices
from maleo_foundation.client.services.hash.bcrypt import MaleoFoundationBcryptHashClientService
from maleo_foundation.client.services.hash.hmac import MaleoFoundationHMACHashClientService
from maleo_foundation.client.services.hash.sha256 import MaleoFoundationSHA256HashClientService

class MaleoFoundationHashServices(ClientServices):
    bcrypt:MaleoFoundationBcryptHashClientService = Field(..., description="Bcrypt hash's service")
    hmac:MaleoFoundationHMACHashClientService = Field(..., description="HMAC hash's service")
    sha256:MaleoFoundationSHA256HashClientService = Field(..., description="SHA256 hash's service")