from maleo_foundation.models.schemas.hash import MaleoFoundationHashSchemas

class MaleoFoundationBcryptHashParametersTransfers:
    class Hash(MaleoFoundationHashSchemas.Message): pass

    class Verify(
        MaleoFoundationHashSchemas.Hash,
        MaleoFoundationHashSchemas.Message
    ): pass