from __future__ import annotations
from .general import BaseGeneralExpandedTypes
from .service import ExpandedServiceTypes
from .client import ExpandedClientTypes


class BaseExpandedTypes:
    General = BaseGeneralExpandedTypes
    Service = ExpandedServiceTypes
    Client = ExpandedClientTypes
