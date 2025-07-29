from typing import Awaitable, Callable, Union
from maleo_foundation.models.transfers.parameters.general \
    import BaseGeneralParametersTransfers
from maleo_foundation.models.transfers.parameters.client \
    import BaseClientParametersTransfers
from maleo_foundation.models.transfers.results.client.service \
    import BaseClientServiceResultsTransfers

class ExpandedClientTypes:
    #* Unpaginated multiple data
    GetUnpaginatedMultipleParameter = BaseClientParametersTransfers.GetUnpaginatedMultiple
    GetUnpaginatedMultipleResult = Union[
        BaseClientServiceResultsTransfers.Fail,
        BaseClientServiceResultsTransfers.NoData,
        BaseClientServiceResultsTransfers.UnpaginatedMultipleData
    ]
    SyncGetUnpaginatedMultipleFunction = Callable[
        [GetUnpaginatedMultipleParameter],
        GetUnpaginatedMultipleResult
    ]
    AsyncGetUnpaginatedMultipleFunction = Callable[
        [GetUnpaginatedMultipleParameter],
        Awaitable[GetUnpaginatedMultipleResult]
    ]

    #* Paginated multiple data
    GetPaginatedMultipleParameter = BaseClientParametersTransfers.GetPaginatedMultiple
    GetPaginatedMultipleResult = Union[
        BaseClientServiceResultsTransfers.Fail,
        BaseClientServiceResultsTransfers.NoData,
        BaseClientServiceResultsTransfers.PaginatedMultipleData
    ]
    SyncGetPaginatedMultipleFunction = Callable[
        [GetPaginatedMultipleParameter],
        GetPaginatedMultipleResult
    ]
    AsyncGetPaginatedMultipleFunction = Callable[
        [GetPaginatedMultipleParameter],
        Awaitable[GetPaginatedMultipleResult]
    ]

    #* Single data
    GetSingleParameter = BaseGeneralParametersTransfers.GetSingle
    GetSingleResult = Union[
        BaseClientServiceResultsTransfers.Fail,
        BaseClientServiceResultsTransfers.NoData,
        BaseClientServiceResultsTransfers.SingleData
    ]
    SyncGetSingleFunction = Callable[
        [GetSingleParameter],
        GetSingleResult
    ]
    AsyncGetSingleFunction = Callable[
        [GetSingleParameter],
        Awaitable[GetSingleResult]
    ]

    #* Create or Update
    CreateOrUpdateResult = Union[
        BaseClientServiceResultsTransfers.Fail,
        BaseClientServiceResultsTransfers.SingleData
    ]

    #* Status Update
    StatusUpdateResult = Union[
        BaseClientServiceResultsTransfers.Fail,
        BaseClientServiceResultsTransfers.SingleData
    ]