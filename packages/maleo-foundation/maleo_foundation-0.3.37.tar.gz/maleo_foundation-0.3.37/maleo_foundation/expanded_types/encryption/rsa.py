from typing import Union
from maleo_foundation.models.transfers.results.encryption.rsa \
    import MaleoFoundationRSAEncryptionResultsTransfers

class MaleoFoundationRSAEncryptionResultsTypes:
    Encrypt = Union[
        MaleoFoundationRSAEncryptionResultsTransfers.Fail,
        MaleoFoundationRSAEncryptionResultsTransfers.Encrypt
    ]

    Decrypt = Union[
        MaleoFoundationRSAEncryptionResultsTransfers.Fail,
        MaleoFoundationRSAEncryptionResultsTransfers.Decrypt
    ]