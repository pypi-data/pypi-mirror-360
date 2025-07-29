from typing import Union
from maleo_foundation.models.transfers.results.signature \
    import MaleoFoundationSignatureResultsTransfers

class MaleoFoundationSignatureResultsTypes:
    Sign = Union[
        MaleoFoundationSignatureResultsTransfers.Fail,
        MaleoFoundationSignatureResultsTransfers.Sign
    ]

    Verify = Union[
        MaleoFoundationSignatureResultsTransfers.Fail,
        MaleoFoundationSignatureResultsTransfers.Verify
    ]