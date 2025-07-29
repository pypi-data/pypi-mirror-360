from Crypto.Hash import HMAC, SHA256
from maleo_foundation.expanded_types.hash \
    import MaleoFoundationHashResultsTypes
from maleo_foundation.managers.client.base import ClientService
from maleo_foundation.models.schemas.hash import \
    MaleoFoundationHashSchemas
from maleo_foundation.models.transfers.parameters.hash.hmac \
    import MaleoFoundationHMACHashParametersTransfers
from maleo_foundation.models.transfers.results.hash \
    import MaleoFoundationHashResultsTransfers
from maleo_foundation.utils.exceptions import BaseExceptions

class MaleoFoundationHMACHashClientService(ClientService):
    def hash(
        self,
        parameters:MaleoFoundationHMACHashParametersTransfers.Hash
    ) -> MaleoFoundationHashResultsTypes.Hash:
        """Generate a hmac hash for the given message."""
        @BaseExceptions.service_exception_handler(
            operation="hashing single message",
            logger=self._logger,
            fail_result_class=MaleoFoundationHashResultsTransfers.Fail
        )
        def _impl():
            hash = HMAC.new(
                key=parameters.key.encode(),
                msg=parameters.message.encode(),
                digestmod=SHA256
            ).hexdigest()
            data = MaleoFoundationHashSchemas.Hash(hash=hash)
            self._logger.info("Message successfully hashed")
            return MaleoFoundationHashResultsTransfers.Hash(data=data)
        return _impl()

    def verify(
        self,
        parameters:MaleoFoundationHMACHashParametersTransfers.Verify
    ) -> MaleoFoundationHashResultsTypes.Verify:
        """Verify a message against the given message hash."""
        @BaseExceptions.service_exception_handler(
            operation="verify single hash",
            logger=self._logger,
            fail_result_class=MaleoFoundationHashResultsTransfers.Fail
        )
        def _impl():
            computed_hash = HMAC.new(
                key=parameters.key.encode(),
                msg=parameters.message.encode(),
                digestmod=SHA256
            ).hexdigest()
            is_valid = computed_hash == parameters.hash
            data = MaleoFoundationHashSchemas.IsValid(is_valid=is_valid)
            self._logger.info("Hash successfully verified")
            return MaleoFoundationHashResultsTransfers.Verify(data=data)
        return _impl()