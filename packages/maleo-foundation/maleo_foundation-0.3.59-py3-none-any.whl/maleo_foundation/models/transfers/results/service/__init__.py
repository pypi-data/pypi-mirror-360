from __future__ import annotations
from .general import BaseServiceGeneralResultsTransfers
from .controllers import BaseServiceControllerResultsTransfers


class BaseServiceResultsTransfers:
    General = BaseServiceGeneralResultsTransfers
    Controller = BaseServiceControllerResultsTransfers
