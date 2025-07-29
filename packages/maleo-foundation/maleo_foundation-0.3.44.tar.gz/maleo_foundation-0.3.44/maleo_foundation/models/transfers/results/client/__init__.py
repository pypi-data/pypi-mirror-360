from __future__ import annotations
from .service import BaseClientServiceResultsTransfers
from .controllers import BaseClientControllersResultsTransfers

class BaseClientResultsTransfers:
    Service = BaseClientServiceResultsTransfers
    Controller = BaseClientControllersResultsTransfers