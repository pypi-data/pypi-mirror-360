from cryptography.hazmat.primitives import serialization
from Crypto.PublicKey import RSA
from pathlib import Path
from typing import Optional, Union
from maleo_foundation.enums import BaseEnums
from maleo_foundation.types import BaseTypes

class RSAKeyLoader:
    @staticmethod
    def load_with_cryptography(
        type:BaseEnums.KeyType,
        data:Optional[Union[bytes, str]] = None,
        path:Optional[Union[str, Path]] = None,
        password:Optional[Union[bytes, str]] = None,
        format:BaseEnums.KeyFormatType = BaseEnums.KeyFormatType.STRING,
    ) -> Union[bytes, str]:
        if not isinstance(type, BaseEnums.KeyType):
            raise TypeError("Invalid key type")

        if data is not None and path is not None:
            raise ValueError("Only either data or path will be accepted as parameters")

        if data is not None:
            if isinstance(data, bytes):
                key_data = data
            elif isinstance(data, str):
                key_data = data.encode()
            else:
                raise TypeError("Invalid data type")

        if path is not None:
            file_path = Path(path)

            if not file_path.exists() or not file_path.is_file():
                raise FileNotFoundError(f"Key file not found: {file_path}")

            key_data = file_path.read_bytes()

        if password is not None and not isinstance(password, (str, bytes)):
            raise TypeError("Invalid passsword type")

        if not isinstance(format, BaseEnums.KeyFormatType):
            raise TypeError("Invalid key format type")

        if type == BaseEnums.KeyType.PRIVATE:
            private_key = serialization.load_pem_private_key(
                key_data,
                password=password.encode() if isinstance(password, str) else password,
            )
            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            if format == BaseEnums.KeyFormatType.BYTES:
                return private_key_bytes
            elif format == BaseEnums.KeyFormatType.STRING:
                return private_key_bytes.decode()

        if type == BaseEnums.KeyType.PUBLIC:
            public_key = serialization.load_pem_public_key(key_data)
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            if format == BaseEnums.KeyFormatType.BYTES:
                return public_key_bytes
            elif format == BaseEnums.KeyFormatType.STRING:
                return public_key_bytes.decode()

    @staticmethod
    def load_with_pycryptodome(
        type:BaseEnums.KeyType,
        extern_key:Union[bytes, str],
        passphrase:BaseTypes.OptionalString = None,
    ) -> RSA.RsaKey:
        if not isinstance(type, BaseEnums.KeyType):
            raise TypeError("Invalid key type")

        if not isinstance(extern_key, (str, bytes)):
            raise TypeError("Invalid external key type")

        if type == BaseEnums.KeyType.PRIVATE:
            private_key = RSA.import_key(extern_key=extern_key, passphrase=passphrase)
            if not private_key.has_private():
                raise TypeError("Invalid chosen key type, the private key did not has private inside it")
            return private_key

        if type == BaseEnums.KeyType.PUBLIC:
            public_key = RSA.import_key(extern_key=extern_key)
            if public_key.has_private():
                raise TypeError("Invalid chosen key type, the public key did has private inside it")
            return public_key