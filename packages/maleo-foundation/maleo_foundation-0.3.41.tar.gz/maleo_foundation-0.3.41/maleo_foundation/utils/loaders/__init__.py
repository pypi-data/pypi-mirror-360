from __future__ import annotations
from .credential import CredentialLoaders
from .json import JSONLoader
from .key import KeyLoaders
from .yaml import YAMLLoader

class BaseLoaders:
    Credential = CredentialLoaders
    JSON = JSONLoader
    Key = KeyLoaders
    YAML = YAMLLoader