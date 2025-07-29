from __future__ import annotations
from .general import BaseGeneralExpandedTypes
from .repository import ExpandedRepositoryTypes
from .service import ExpandedServiceTypes
from .client import ExpandedClientTypes

class BaseExpandedTypes:
    General = BaseGeneralExpandedTypes
    Repository = ExpandedRepositoryTypes
    Service = ExpandedServiceTypes
    Client = ExpandedClientTypes