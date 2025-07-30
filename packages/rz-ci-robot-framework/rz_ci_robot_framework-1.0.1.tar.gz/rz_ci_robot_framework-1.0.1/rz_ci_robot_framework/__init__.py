"""
RZ-CI Robot Framework - Board testing framework for Renesas RZ boards

This package provides a comprehensive testing framework for Renesas RZ boards
using Robot Framework. It includes:

- Dynamic configuration system based on YAML
- Feature-specific test libraries (I2C, SPI, GPIO, etc.)
- Board-specific test generation
- Serial communication management
- Comprehensive reporting and logging
"""

from .version import __version__

__all__ = [
    '__version__',
]

# Package metadata
__author__ = "RZ-CI Team"
__email__ = "rz-ci@renesas.com"
__license__ = "MIT"
__copyright__ = "Copyright 2024 Renesas Electronics Corporation"
