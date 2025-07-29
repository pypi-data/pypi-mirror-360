from __future__ import annotations
from .general import BaseGeneralParametersTransfers
from .service import BaseServiceParametersTransfers
from .client import BaseClientParametersTransfers

class BaseParametersTransfers:
    General = BaseGeneralParametersTransfers
    Service = BaseServiceParametersTransfers
    Client = BaseClientParametersTransfers