from __future__ import annotations
from .formatter import BaseFormatter
from .loaders import BaseLoaders
from .controller import BaseControllerUtils
from .query import BaseQueryUtils


class BaseUtils:
    Formatter = BaseFormatter
    Loaders = BaseLoaders
    Controller = BaseControllerUtils
    Query = BaseQueryUtils
