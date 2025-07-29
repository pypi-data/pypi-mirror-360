from __future__ import annotations
from .aes import MaleoFoundationAESEncryptionParametersTransfers
from .rsa import MaleoFoundationRSAEncryptionParametersTransfers

class BaseEncryptionParametersTransfers:
    AES = MaleoFoundationAESEncryptionParametersTransfers
    RSA = MaleoFoundationRSAEncryptionParametersTransfers