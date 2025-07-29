from __future__ import annotations
from pydantic import Field
from maleo_foundation.managers.client.base import ClientServices
from maleo_foundation.client.services.encryption import MaleoFoundationEncryptionServices
from maleo_foundation.client.services.hash import MaleoFoundationHashServices
from maleo_foundation.client.services.key import MaleoFoundationKeyClientService
from maleo_foundation.client.services.signature import MaleoFoundationSignatureClientService
from maleo_foundation.client.services.token import MaleoFoundationTokenClientService

class MaleoFoundationServices(ClientServices):
    encryption:MaleoFoundationEncryptionServices = Field(..., description="Encryption's services")
    hash:MaleoFoundationHashServices = Field(..., description="Hash's services")
    key:MaleoFoundationKeyClientService = Field(..., description="Key's service")
    signature:MaleoFoundationSignatureClientService = Field(..., description="Signature's service")
    token:MaleoFoundationTokenClientService = Field(..., description="Token's service")