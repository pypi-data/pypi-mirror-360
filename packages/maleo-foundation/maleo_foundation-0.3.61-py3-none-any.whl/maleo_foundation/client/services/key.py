from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from maleo_foundation.enums import BaseEnums
from maleo_foundation.expanded_types.key import MaleoFoundationKeyResultsTypes
from maleo_foundation.managers.client.base import ClientService
from maleo_foundation.models.transfers.general.key import (
    MaleoFoundationKeyGeneralTransfers,
)
from maleo_foundation.models.transfers.parameters.key import (
    MaleoFoundationKeyParametersTransfers,
)
from maleo_foundation.models.transfers.results.key import (
    MaleoFoundationKeyResultsTransfers,
)
from maleo_foundation.utils.exceptions.service import BaseServiceExceptions


RESOURCE = "keys"


class MaleoFoundationKeyClientService(ClientService):
    def create_private(
        self, parameters: MaleoFoundationKeyParametersTransfers.CreatePrivateOrPair
    ) -> MaleoFoundationKeyResultsTypes.CreatePrivate:
        """Create an RSA private key with X.509 encoding in .pem format."""

        @BaseServiceExceptions.sync_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            target=BaseEnums.OperationTarget.INTERNAL,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.CREATE,
            create_type=BaseEnums.CreateType.CREATE,
            summary="creating private key",
            logger=self._logger,
            fail_result_class=MaleoFoundationKeyResultsTransfers.Fail,
        )
        def _impl():
            # * Create private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=parameters.key_size,
                backend=default_backend(),
            )

            if parameters.password is None:
                encryption_algorithm = serialization.NoEncryption()
            else:
                encryption_algorithm = serialization.BestAvailableEncryption(
                    parameters.password.encode()
                )

            # * Serialize private key to PEM format
            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption_algorithm,
            )

            self._logger.info("Successfully created private key")
            data = MaleoFoundationKeyGeneralTransfers.PrivateKey(
                value=private_key_bytes.decode()
            )  # type: ignore
            return MaleoFoundationKeyResultsTransfers.CreatePrivate(
                origin=BaseEnums.OperationOrigin.CLIENT,
                layer=BaseEnums.OperationLayer.SERVICE,
                target=BaseEnums.OperationTarget.INTERNAL,
                resource=RESOURCE,
                operation=BaseEnums.OperationType.CREATE,
                create_type=BaseEnums.CreateType.CREATE,
                data=data,
            )  # type: ignore

        return _impl()

    def create_public(
        self, parameters: MaleoFoundationKeyParametersTransfers.CreatePublic
    ) -> MaleoFoundationKeyResultsTypes.CreatePublic:
        """Create an RSA public key with X.509 encoding in .pem format."""

        @BaseServiceExceptions.sync_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            target=BaseEnums.OperationTarget.INTERNAL,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.CREATE,
            create_type=BaseEnums.CreateType.CREATE,
            summary="creating public key",
            logger=self._logger,
            fail_result_class=MaleoFoundationKeyResultsTransfers.Fail,
        )
        def _impl():
            # * Serialize private key
            private_key_bytes = parameters.value.encode()
            private_key = serialization.load_pem_private_key(
                private_key_bytes,
                password=parameters.password.encode() if parameters.password else None,
                backend=default_backend(),
            )

            public_key = private_key.public_key()  # * Create public key

            # * Serialize public key to PEM format
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            self._logger.info("Successfully created public key")
            data = MaleoFoundationKeyGeneralTransfers.PublicKey(
                value=public_key_bytes.decode()
            )  # type: ignore
            return MaleoFoundationKeyResultsTransfers.CreatePublic(
                origin=BaseEnums.OperationOrigin.CLIENT,
                layer=BaseEnums.OperationLayer.SERVICE,
                target=BaseEnums.OperationTarget.INTERNAL,
                resource=RESOURCE,
                operation=BaseEnums.OperationType.CREATE,
                create_type=BaseEnums.CreateType.CREATE,
                data=data,
            )  # type: ignore

        return _impl()

    def create_pair(
        self, parameters: MaleoFoundationKeyParametersTransfers.CreatePrivateOrPair
    ) -> MaleoFoundationKeyResultsTypes.CreatePair:
        """Create an RSA key pair with X.509 encoding in .pem format."""

        @BaseServiceExceptions.sync_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            target=BaseEnums.OperationTarget.INTERNAL,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.CREATE,
            create_type=BaseEnums.CreateType.CREATE,
            summary="creating key pair",
            logger=self._logger,
            fail_result_class=MaleoFoundationKeyResultsTransfers.Fail,
        )
        def _impl():
            # * Create private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=parameters.key_size,
                backend=default_backend(),
            )

            if parameters.password is None:
                encryption_algorithm = serialization.NoEncryption()
            else:
                encryption_algorithm = serialization.BestAvailableEncryption(
                    parameters.password.encode()
                )

            # * Serialize private key to PEM format
            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption_algorithm,
            )
            private = MaleoFoundationKeyGeneralTransfers.PrivateKey(
                value=private_key_bytes.decode()
            )  # type: ignore

            public_key = private_key.public_key()  # * Create public key

            # * Serialize public key to PEM format
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            public = MaleoFoundationKeyGeneralTransfers.PublicKey(
                value=public_key_bytes.decode()
            )  # type: ignore

            self._logger.info("Successfully created key pair")
            data = MaleoFoundationKeyGeneralTransfers.KeyPair(
                private=private, public=public
            )
            return MaleoFoundationKeyResultsTransfers.CreatePair(
                origin=BaseEnums.OperationOrigin.CLIENT,
                layer=BaseEnums.OperationLayer.SERVICE,
                target=BaseEnums.OperationTarget.INTERNAL,
                resource=RESOURCE,
                operation=BaseEnums.OperationType.CREATE,
                create_type=BaseEnums.CreateType.CREATE,
                data=data,
            )  # type: ignore

        return _impl()
