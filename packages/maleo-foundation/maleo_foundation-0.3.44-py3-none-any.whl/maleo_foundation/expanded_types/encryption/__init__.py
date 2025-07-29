from __future__ import annotations
from .aes import MaleoFoundationAESEncryptionResultsTransfers
from .rsa import MaleoFoundationRSAEncryptionResultsTransfers

class BaseEncryptionResultsTypes:
    AES = MaleoFoundationAESEncryptionResultsTransfers
    RSA = MaleoFoundationRSAEncryptionResultsTransfers