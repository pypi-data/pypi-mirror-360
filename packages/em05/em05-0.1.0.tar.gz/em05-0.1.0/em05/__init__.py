"""
EM05 SMS Library

A Python library for communicating with Quectel EM05 cellular modules via AT commands.
"""

from .em05 import EM05, EM05Resp, SMSMessage

__version__ = "0.1.0"
__author__ = "Rikki"
__email__ = "i@rikki.moe"
__description__ = "Python library for Quectel EM05 cellular module SMS operations"

__all__ = ["EM05", "EM05Resp", "SMSMessage"]