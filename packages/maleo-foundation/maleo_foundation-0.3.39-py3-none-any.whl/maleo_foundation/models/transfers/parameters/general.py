from __future__ import annotations
from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_foundation.models.schemas.parameter import BaseParameterSchemas

class BaseGeneralParametersTransfers:
    class FieldExpansionProcessor(
        BaseParameterSchemas.Expand,
        BaseParameterSchemas.Data
    ): pass

    class FieldModificationProcessor(BaseParameterSchemas.Data): pass

    class GetSingleQuery(BaseParameterSchemas.OptionalListOfStatuses): pass

    class BaseGetSingle(
        BaseParameterSchemas.IdentifierValue,
        BaseParameterSchemas.IdentifierType
    ): pass

    class GetSingle(
        BaseParameterSchemas.OptionalListOfStatuses,
        BaseGetSingle
    ): pass

    class StatusUpdate(BaseGeneralSchemas.Status): pass