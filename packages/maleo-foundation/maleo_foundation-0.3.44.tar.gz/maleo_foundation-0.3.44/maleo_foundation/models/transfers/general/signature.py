from __future__ import annotations
from maleo_foundation.models.schemas.signature import MaleoFoundationSignatureSchemas

class BaseSignatureGeneralTransfers:
    class SignaturePackage(
        MaleoFoundationSignatureSchemas.Message,
        MaleoFoundationSignatureSchemas.Signature
    ): pass