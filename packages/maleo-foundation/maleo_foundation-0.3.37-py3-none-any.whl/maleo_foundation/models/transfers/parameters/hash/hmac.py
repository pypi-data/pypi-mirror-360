from maleo_foundation.models.schemas.hash import MaleoFoundationHashSchemas

class MaleoFoundationHMACHashParametersTransfers:
    class Hash(
        MaleoFoundationHashSchemas.Message,
        MaleoFoundationHashSchemas.Key
    ): pass

    class Verify(
        MaleoFoundationHashSchemas.Hash,
        MaleoFoundationHashSchemas.Message,
        MaleoFoundationHashSchemas.Key
    ): pass