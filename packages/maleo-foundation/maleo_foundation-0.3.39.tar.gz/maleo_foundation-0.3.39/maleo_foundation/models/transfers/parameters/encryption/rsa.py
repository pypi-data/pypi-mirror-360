from maleo_foundation.models.schemas.encryption import MaleoFoundationEncryptionSchemas

class MaleoFoundationRSAEncryptionParametersTransfers:
    class Encrypt(
        MaleoFoundationEncryptionSchemas.Plaintext,
        MaleoFoundationEncryptionSchemas.Key
    ): pass

    class Decrypt(
        MaleoFoundationEncryptionSchemas.Ciphertext,
        MaleoFoundationEncryptionSchemas.Password,
        MaleoFoundationEncryptionSchemas.Key
    ): pass