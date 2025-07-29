from maleo_foundation.models.schemas.encryption import MaleoFoundationEncryptionSchemas

class MaleoFoundationAESEncryptionParametersTransfers:
    class Encrypt(
        MaleoFoundationEncryptionSchemas.Plaintext,
        MaleoFoundationEncryptionSchemas.Key
    ): pass

    class Decrypt(
        MaleoFoundationEncryptionSchemas.Ciphertext,
        MaleoFoundationEncryptionSchemas.InitializationVector,
        MaleoFoundationEncryptionSchemas.Key
    ): pass