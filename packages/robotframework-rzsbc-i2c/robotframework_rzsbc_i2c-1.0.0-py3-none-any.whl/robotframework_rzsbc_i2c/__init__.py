"""
robotframework-rzsbc-i2c - Robot Framework Library for RZ-SBC I2C communication

This library provides keywords for I2C communication with dynamic board configuration
support for Renesas RZ-SBC systems.
"""

__version__ = "1.0.0"
__author__ = "RZ-CI Team"
__email__ = "rz-ci@renesas.com"

from .I2CLibrary.I2CLibrary import I2CLibrary

__all__ = [
    'I2CLibrary',
]
