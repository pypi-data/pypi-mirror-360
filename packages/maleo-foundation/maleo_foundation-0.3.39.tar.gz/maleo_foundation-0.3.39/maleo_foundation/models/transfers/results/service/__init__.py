from __future__ import annotations
from .general import BaseServiceGeneralResultsTransfers
from .repository import BaseServiceRepositoryResultsTransfers
from .controllers import BaseServiceControllerResultsTransfers

class BaseServiceResultsTransfers:
    General = BaseServiceGeneralResultsTransfers
    Repository = BaseServiceRepositoryResultsTransfers
    Controller = BaseServiceControllerResultsTransfers