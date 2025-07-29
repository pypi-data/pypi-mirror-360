from __future__ import annotations
from .general import BaseGeneralTransfers
from .parameters import BaseParametersTransfers
from .results import BaseResultsTransfers

class BaseTransfers:
    General = BaseGeneralTransfers
    Parameters = BaseParametersTransfers
    Results = BaseResultsTransfers