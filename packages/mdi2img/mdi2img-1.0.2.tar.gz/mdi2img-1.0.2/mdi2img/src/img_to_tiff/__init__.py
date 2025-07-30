"""
This module provides a class to convert MDI files to TIFF format.
It imports the MDIToTiff class from the mdi_to_tiff module, which contains the logic for the conversion process.
The MDIToTiff class is the main entry point for users to convert MDI files to TIFF format.
"""
from .mdi_to_tiff import MDIToTiff

__all__ = ["MDIToTiff"]
