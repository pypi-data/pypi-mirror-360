"""
robotframework-rzsbc-i2c - Robot Framework Library for RZ-SBC I2C communication

This library provides keywords for I2C communication with dynamic board configuration
support for Renesas RZ-SBC systems.
"""

__version__ = "1.0.1"
__author__ = "RZ-CI Team"
__email__ = "rz-ci@renesas.com"

# Import the I2CLibrary class directly at package level
from .I2CLibrary.I2CLibrary import I2CLibrary

# Make I2CLibrary available as the main library class
# This allows: Library    robotframework_rzsbc_i2c
# Robot Framework will automatically find the I2CLibrary class
__all__ = [
    'I2CLibrary',
]

# Make the library class available at the top level
# This enables both import styles:
# 1. Library    robotframework_rzsbc_i2c
# 2. Library    robotframework_rzsbc_i2c.I2CLibrary
def get_library():
    """Return the main library class for Robot Framework"""
    return I2CLibrary
