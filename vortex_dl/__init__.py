"""
Vortex-DL: High-Performance Asynchronous Multi-part Downloader.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sebuah tool CLI untuk mengunduh file dengan kecepatan maksimal 
menggunakan teknik multi-part concurrency dan UI terminal yang estetik.
"""

from .core import VortexCore
from .ui import VortexUI

__version__ = "1.3.0"
__author__ = "Smile Of Beauty"

__all__ = ["VortexCore", "VortexUI"]