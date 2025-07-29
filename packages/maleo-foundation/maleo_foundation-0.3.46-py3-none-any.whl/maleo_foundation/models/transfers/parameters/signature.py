from maleo_foundation.models.schemas.signature import MaleoFoundationSignatureSchemas

class MaleoFoundationSignatureParametersTransfers:
    class Sign(
        MaleoFoundationSignatureSchemas.Message,
        MaleoFoundationSignatureSchemas.Password,
        MaleoFoundationSignatureSchemas.Key
    ): pass

    class Verify(
        MaleoFoundationSignatureSchemas.Signature,
        MaleoFoundationSignatureSchemas.Message,
        MaleoFoundationSignatureSchemas.Key
    ): pass