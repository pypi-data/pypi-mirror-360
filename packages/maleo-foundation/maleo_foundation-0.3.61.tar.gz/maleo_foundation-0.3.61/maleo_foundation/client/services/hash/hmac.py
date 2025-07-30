from Crypto.Hash import HMAC, SHA256
from maleo_foundation.enums import BaseEnums
from maleo_foundation.expanded_types.hash import MaleoFoundationHashResultsTypes
from maleo_foundation.managers.client.base import ClientService
from maleo_foundation.models.schemas.hash import MaleoFoundationHashSchemas
from maleo_foundation.models.transfers.parameters.hash.hmac import (
    MaleoFoundationHMACHashParametersTransfers,
)
from maleo_foundation.models.transfers.results.hash import (
    MaleoFoundationHashResultsTransfers,
)
from maleo_foundation.utils.exceptions.service import BaseServiceExceptions


RESOURCE = "hmac_hashes"


class MaleoFoundationHMACHashClientService(ClientService):
    def hash(
        self, parameters: MaleoFoundationHMACHashParametersTransfers.Hash
    ) -> MaleoFoundationHashResultsTypes.Hash:
        """Generate a hmac hash for the given message."""

        @BaseServiceExceptions.sync_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            target=BaseEnums.OperationTarget.INTERNAL,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.CREATE,
            create_type=BaseEnums.CreateType.CREATE,
            summary="hashing single message",
            logger=self._logger,
            fail_result_class=MaleoFoundationHashResultsTransfers.Fail,
        )
        def _impl():
            hash = HMAC.new(
                key=parameters.key.encode(),
                msg=parameters.message.encode(),
                digestmod=SHA256,
            ).hexdigest()
            data = MaleoFoundationHashSchemas.Hash(hash=hash)
            self._logger.info("Message successfully hashed")
            return MaleoFoundationHashResultsTransfers.Hash(
                origin=BaseEnums.OperationOrigin.CLIENT,
                layer=BaseEnums.OperationLayer.SERVICE,
                target=BaseEnums.OperationTarget.INTERNAL,
                resource=RESOURCE,
                operation=BaseEnums.OperationType.CREATE,
                create_type=BaseEnums.CreateType.CREATE,
                data=data,
            )  # type: ignore

        return _impl()

    def verify(
        self, parameters: MaleoFoundationHMACHashParametersTransfers.Verify
    ) -> MaleoFoundationHashResultsTypes.Verify:
        """Verify a message against the given message hash."""

        @BaseServiceExceptions.sync_exception_handler(
            layer=BaseEnums.OperationLayer.SERVICE,
            target=BaseEnums.OperationTarget.INTERNAL,
            resource=RESOURCE,
            operation=BaseEnums.OperationType.CREATE,
            create_type=BaseEnums.CreateType.CREATE,
            summary="verify single hash",
            logger=self._logger,
            fail_result_class=MaleoFoundationHashResultsTransfers.Fail,
        )
        def _impl():
            computed_hash = HMAC.new(
                key=parameters.key.encode(),
                msg=parameters.message.encode(),
                digestmod=SHA256,
            ).hexdigest()
            is_valid = computed_hash == parameters.hash
            data = MaleoFoundationHashSchemas.IsValid(is_valid=is_valid)
            self._logger.info("Hash successfully verified")
            return MaleoFoundationHashResultsTransfers.Verify(
                origin=BaseEnums.OperationOrigin.CLIENT,
                layer=BaseEnums.OperationLayer.SERVICE,
                target=BaseEnums.OperationTarget.INTERNAL,
                resource=RESOURCE,
                operation=BaseEnums.OperationType.CREATE,
                create_type=BaseEnums.CreateType.CREATE,
                data=data,
            )  # type: ignore

        return _impl()
