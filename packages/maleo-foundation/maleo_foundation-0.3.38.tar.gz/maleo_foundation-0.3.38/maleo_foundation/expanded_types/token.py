from typing import Union
from maleo_foundation.models.transfers.results.token \
    import MaleoFoundationTokenResultsTransfers

class MaleoFoundationTokenResultsTypes:
    Encode = Union[
        MaleoFoundationTokenResultsTransfers.Fail,
        MaleoFoundationTokenResultsTransfers.Encode
    ]

    Decode = Union[
        MaleoFoundationTokenResultsTransfers.Fail,
        MaleoFoundationTokenResultsTransfers.Decode
    ]