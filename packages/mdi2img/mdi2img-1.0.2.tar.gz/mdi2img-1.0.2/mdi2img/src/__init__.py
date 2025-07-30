"""
File in charge of linking the different elements of the program so that it can be easily imported by the root of the program
"""

from .convert_to_any import ChangeImageFormat, AVAILABLE_FORMATS, AVAILABLE_FORMATS_HELP
from .img_to_tiff import MDIToTiff
from .viewer import ViewImage
from .globals import LOG, SUCCESS, ERROR, ERR, SELECTED_LIST, SPLASH_NAME, SPLASH, __version__, __author__, Constants
from .main import Main

__all__ = [
    "MDIToTiff",
    "ChangeImageFormat",
    "AVAILABLE_FORMATS",
    "AVAILABLE_FORMATS_HELP",
    "ViewImage",
    "LOG",
    "SUCCESS",
    "ERROR",
    "ERR",
    "SELECTED_LIST",
    "SPLASH_NAME",
    "SPLASH",
    "__version__",
    "__author__",
    "Constants",
    "Main"
]
