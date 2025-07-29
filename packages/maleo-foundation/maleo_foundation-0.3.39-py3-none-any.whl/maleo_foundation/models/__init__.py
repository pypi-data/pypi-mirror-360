from __future__ import annotations
from .schemas import BaseSchemas
from .transfers import BaseTransfers
from .responses import BaseResponses

class BaseModels:
    Schemas = BaseSchemas
    Transfers = BaseTransfers
    Responses = BaseResponses