from __future__ import annotations
from .bcrypt import MaleoFoundationBcryptHashParametersTransfers
from .hmac import MaleoFoundationHMACHashParametersTransfers
from .sha256 import MaleoFoundationSHA256HashParametersTransfers

class BaseHashParametersTransfers:
    Bcrypt = MaleoFoundationBcryptHashParametersTransfers
    HMAC = MaleoFoundationHMACHashParametersTransfers
    SHA256 = MaleoFoundationSHA256HashParametersTransfers