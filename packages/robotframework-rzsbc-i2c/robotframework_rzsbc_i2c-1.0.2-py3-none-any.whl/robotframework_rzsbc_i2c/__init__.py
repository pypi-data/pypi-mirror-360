"""
robotframework-rzsbc-i2c - Robot Framework Library for RZ-SBC I2C communication

This library provides keywords for I2C communication with dynamic board configuration
support for Renesas RZ-SBC systems.
"""

__version__ = "1.0.2"
__author__ = "RZ-CI Team"
__email__ = "rz-ci@renesas.com"

# Import the I2CLibrary class and make it available at package level
from .I2CLibrary.I2CLibrary import I2CLibrary

# For Robot Framework direct import support, expose the library class
# This allows: Library    robotframework_rzsbc_i2c
__all__ = ['I2CLibrary']

# Robot Framework will look for these attributes when importing directly
def get_library_instance():
    """Return library instance for Robot Framework"""
    return I2CLibrary()

# Alternative: Make the class available as module attribute
import sys
sys.modules[__name__].__class__ = type('Module', (), {
    '__getattr__': lambda self, name: getattr(I2CLibrary(), name) if hasattr(I2CLibrary(), name) else getattr(sys.modules[__name__], name)
})
