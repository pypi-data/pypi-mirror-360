from typing import Union
from maleo_foundation.models.transfers.results.key \
    import MaleoFoundationKeyResultsTransfers

class MaleoFoundationKeyResultsTypes:
    CreatePrivate = Union[
        MaleoFoundationKeyResultsTransfers.Fail,
        MaleoFoundationKeyResultsTransfers.CreatePrivate
    ]

    CreatePublic = Union[
        MaleoFoundationKeyResultsTransfers.Fail,
        MaleoFoundationKeyResultsTransfers.CreatePublic
    ]

    CreatePair = Union[
        MaleoFoundationKeyResultsTransfers.Fail,
        MaleoFoundationKeyResultsTransfers.CreatePair
    ]