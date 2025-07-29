from __future__ import annotations
from pydantic import Field
from maleo_foundation.managers.client.base import ClientServices
from maleo_foundation.client.services.encryption.aes import MaleoFoundationAESEncryptionClientService
from maleo_foundation.client.services.encryption.rsa import MaleoFoundationRSAEncryptionClientService

class MaleoFoundationEncryptionServices(ClientServices):
    aes:MaleoFoundationAESEncryptionClientService = Field(..., description="AES encryption's service")
    rsa:MaleoFoundationRSAEncryptionClientService = Field(..., description="RSA encryption's service")