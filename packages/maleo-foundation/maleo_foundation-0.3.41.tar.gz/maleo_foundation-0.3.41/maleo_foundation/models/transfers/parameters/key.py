from maleo_foundation.models.schemas.key import BaseKeySchemas
from maleo_foundation.models.transfers.general.key import MaleoFoundationKeyGeneralTransfers

class MaleoFoundationKeyParametersTransfers:
    class CreatePrivateOrPair(
        BaseKeySchemas.Password,
        BaseKeySchemas.KeySize
    ): pass

    class CreatePublic(
        BaseKeySchemas.Password,
        MaleoFoundationKeyGeneralTransfers.PrivateKey
    ): pass