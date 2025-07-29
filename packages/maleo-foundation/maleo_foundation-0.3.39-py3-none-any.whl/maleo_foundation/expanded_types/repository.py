from typing import Awaitable, Callable, Union
from maleo_foundation.models.transfers.parameters.general \
    import BaseGeneralParametersTransfers
from maleo_foundation.models.transfers.parameters.service \
    import BaseServiceParametersTransfers
from maleo_foundation.models.transfers.results.service.repository \
    import BaseServiceRepositoryResultsTransfers

class ExpandedRepositoryTypes:
    #* Unpaginated multiple data
    GetUnpaginatedMultipleParameter = BaseServiceParametersTransfers.GetUnpaginatedMultiple
    GetUnpaginatedMultipleResult = Union[
        BaseServiceRepositoryResultsTransfers.Fail,
        BaseServiceRepositoryResultsTransfers.NoData,
        BaseServiceRepositoryResultsTransfers.UnpaginatedMultipleData
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
    GetPaginatedMultipleParameter = BaseServiceParametersTransfers.GetPaginatedMultiple
    GetPaginatedMultipleResult = Union[
        BaseServiceRepositoryResultsTransfers.Fail,
        BaseServiceRepositoryResultsTransfers.NoData,
        BaseServiceRepositoryResultsTransfers.PaginatedMultipleData
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
        BaseServiceRepositoryResultsTransfers.Fail,
        BaseServiceRepositoryResultsTransfers.NoData,
        BaseServiceRepositoryResultsTransfers.SingleData
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
        BaseServiceRepositoryResultsTransfers.Fail,
        BaseServiceRepositoryResultsTransfers.SingleData
    ]

    #* Status update
    StatusUpdateResult = Union[
        BaseServiceRepositoryResultsTransfers.Fail,
        BaseServiceRepositoryResultsTransfers.SingleData
    ]