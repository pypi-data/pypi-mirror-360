import bcrypt
from maleo_foundation.expanded_types.hash \
    import MaleoFoundationHashResultsTypes
from maleo_foundation.managers.client.base import ClientService
from maleo_foundation.models.schemas.hash import \
    MaleoFoundationHashSchemas
from maleo_foundation.models.transfers.parameters.hash.bcrypt \
    import MaleoFoundationBcryptHashParametersTransfers
from maleo_foundation.models.transfers.results.hash \
    import MaleoFoundationHashResultsTransfers
from maleo_foundation.utils.exceptions import BaseExceptions

class MaleoFoundationBcryptHashClientService(ClientService):
    def hash(
        self,
        parameters:MaleoFoundationBcryptHashParametersTransfers.Hash
    ) -> MaleoFoundationHashResultsTypes.Hash:
        """Generate a bcrypt hash for the given message."""
        @BaseExceptions.service_exception_handler(
            operation="hashing single message",
            logger=self._logger,
            fail_result_class=MaleoFoundationHashResultsTransfers.Fail
        )
        def _impl():
            hash = bcrypt.hashpw(
                password=parameters.message.encode(),
                salt=bcrypt.gensalt()
            ).decode()
            data = MaleoFoundationHashSchemas.Hash(hash=hash)
            self._logger.info("Message successfully hashed")
            return MaleoFoundationHashResultsTransfers.Hash(data=data)
        return _impl()

    def verify(
        self,
        parameters:MaleoFoundationBcryptHashParametersTransfers.Verify
    ) -> MaleoFoundationHashResultsTypes.Verify:
        """Verify a message against the given message hash."""
        @BaseExceptions.service_exception_handler(
            operation="verify single hash",
            logger=self._logger,
            fail_result_class=MaleoFoundationHashResultsTransfers.Fail
        )
        def _impl():
            is_valid = bcrypt.checkpw(
                password=parameters.message.encode(),
                hashed_password=parameters.hash.encode()
            )
            data = MaleoFoundationHashSchemas.IsValid(is_valid=is_valid)
            self._logger.info("Hash successfully verified")
            return MaleoFoundationHashResultsTransfers.Verify(data=data)
        return _impl()