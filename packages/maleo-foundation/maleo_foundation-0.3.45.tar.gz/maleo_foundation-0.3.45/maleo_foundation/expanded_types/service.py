from typing import Awaitable, Callable, Union
from maleo_foundation.models.transfers.parameters.general \
    import BaseGeneralParametersTransfers
from maleo_foundation.models.transfers.parameters.service \
    import BaseServiceParametersTransfers
from maleo_foundation.models.transfers.results.service.general \
    import BaseServiceGeneralResultsTransfers

class ExpandedServiceTypes:
    #* Unpaginated multiple data
    GetUnpaginatedMultipleParameter = BaseServiceParametersTransfers.GetUnpaginatedMultiple
    GetUnpaginatedMultipleResult = Union[
        BaseServiceGeneralResultsTransfers.Fail,
        BaseServiceGeneralResultsTransfers.NoData,
        BaseServiceGeneralResultsTransfers.UnpaginatedMultipleData
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
        BaseServiceGeneralResultsTransfers.Fail,
        BaseServiceGeneralResultsTransfers.NoData,
        BaseServiceGeneralResultsTransfers.PaginatedMultipleData
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
        BaseServiceGeneralResultsTransfers.Fail,
        BaseServiceGeneralResultsTransfers.NoData,
        BaseServiceGeneralResultsTransfers.SingleData
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
        BaseServiceGeneralResultsTransfers.Fail,
        BaseServiceGeneralResultsTransfers.SingleData
    ]

    #* Status update
    StatusUpdateResult = Union[
        BaseServiceGeneralResultsTransfers.Fail,
        BaseServiceGeneralResultsTransfers.SingleData
    ]