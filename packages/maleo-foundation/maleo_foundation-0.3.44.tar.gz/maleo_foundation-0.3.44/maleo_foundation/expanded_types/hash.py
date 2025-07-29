from typing import Union
from maleo_foundation.models.transfers.results.hash \
    import MaleoFoundationHashResultsTransfers

class MaleoFoundationHashResultsTypes:
    Hash = Union[
        MaleoFoundationHashResultsTransfers.Fail,
        MaleoFoundationHashResultsTransfers.Hash
    ]

    Verify = Union[
        MaleoFoundationHashResultsTransfers.Fail,
        MaleoFoundationHashResultsTransfers.Verify
    ]