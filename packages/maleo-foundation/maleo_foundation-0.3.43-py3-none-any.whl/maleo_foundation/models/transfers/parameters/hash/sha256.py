from maleo_foundation.models.schemas.hash import MaleoFoundationHashSchemas

class MaleoFoundationSHA256HashParametersTransfers:
    class Hash(MaleoFoundationHashSchemas.Message): pass

    class Verify(
        MaleoFoundationHashSchemas.Hash,
        MaleoFoundationHashSchemas.Message
    ): pass