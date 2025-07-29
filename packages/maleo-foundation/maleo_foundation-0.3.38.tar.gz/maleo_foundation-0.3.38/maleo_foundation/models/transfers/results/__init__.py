from __future__ import annotations
from .service import BaseServiceResultsTransfers
from .client import BaseClientResultsTransfers

class BaseResultsTransfers:
    Service = BaseServiceResultsTransfers
    Client = BaseClientResultsTransfers