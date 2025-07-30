"""
File in charge of linking the ressources that are global knowledge to the program
"""

from . import logo as LOG
from .constants import SUCCESS, ERROR, ERR, SELECTED_LIST, SPLASH_NAME, SPLASH, __version__, __author__, Constants

__all__ = [
    "LOG",
    "SUCCESS",
    "ERROR",
    "ERR",
    "SELECTED_LIST",
    "SPLASH_NAME",
    "SPLASH",
    "__version__",
    "__author__",
    "Constants"
]
