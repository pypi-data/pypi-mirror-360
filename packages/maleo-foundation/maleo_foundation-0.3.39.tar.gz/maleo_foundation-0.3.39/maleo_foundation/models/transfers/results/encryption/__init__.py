from __future__ import annotations
from .aes import MaleoFoundationAESEncryptionResultsTransfers
from .rsa import MaleoFoundationRSAEncryptionResultsTransfers

class BaseEncryptionResultsTransfers:
    AES = MaleoFoundationAESEncryptionResultsTransfers
    RSA = MaleoFoundationRSAEncryptionResultsTransfers