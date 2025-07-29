from typing import Union
from maleo_foundation.models.transfers.results.encryption.aes \
    import MaleoFoundationAESEncryptionResultsTransfers

class MaleoFoundationAESEncryptionResultsTypes:
    Encrypt = Union[
        MaleoFoundationAESEncryptionResultsTransfers.Fail,
        MaleoFoundationAESEncryptionResultsTransfers.Encrypt
    ]

    Decrypt = Union[
        MaleoFoundationAESEncryptionResultsTransfers.Fail,
        MaleoFoundationAESEncryptionResultsTransfers.Decrypt
    ]