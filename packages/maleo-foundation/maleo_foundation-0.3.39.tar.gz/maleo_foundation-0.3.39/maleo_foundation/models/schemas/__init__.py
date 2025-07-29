from __future__ import annotations
from .general import BaseGeneralSchemas
from .parameter import BaseParameterSchemas
from .result import BaseResultSchemas

class BaseSchemas:
    General = BaseGeneralSchemas
    Parameter = BaseParameterSchemas
    Result = BaseResultSchemas