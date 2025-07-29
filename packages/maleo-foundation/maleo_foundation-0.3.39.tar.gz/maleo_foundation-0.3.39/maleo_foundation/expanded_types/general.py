from typing import Callable, List, Optional
from maleo_foundation.types import BaseTypes
from maleo_foundation.models.transfers.parameters.general \
    import BaseGeneralParametersTransfers

class BaseGeneralExpandedTypes:
    #* Expansion processor related types
    FieldExpansionProcessor = Callable[
        [BaseGeneralParametersTransfers.FieldExpansionProcessor],
        BaseTypes.ListOrDictOfAny
    ]

    ListOfFieldExpansionProcessor = List[
        Callable[
            [BaseGeneralParametersTransfers.FieldExpansionProcessor],
            BaseTypes.ListOrDictOfAny
        ]
    ]

    OptionalListOfFieldExpansionProcessor = Optional[
        List[
            Callable[
                [BaseGeneralParametersTransfers.FieldExpansionProcessor],
                BaseTypes.ListOrDictOfAny
            ]
        ]
    ]

    #* Modification processor related types
    FieldModificationProcessor = Callable[
        [BaseGeneralParametersTransfers.FieldModificationProcessor],
        BaseTypes.ListOrDictOfAny
    ]

    ListOfFieldModificationProcessor = List[
        Callable[
            [BaseGeneralParametersTransfers.FieldModificationProcessor],
            BaseTypes.ListOrDictOfAny
        ]
    ]

    OptionalListOfFieldModificationProcessor = Optional[
        List[
            Callable[
                [BaseGeneralParametersTransfers.FieldModificationProcessor],
                BaseTypes.ListOrDictOfAny
            ]
        ]
    ]