"""
    This is the file that will be executed when the user runs the module from the command line.
    It will import the Main class from the src.main module and run the main function.
"""

import os
import sys

try:
    from src.main import Main
except ImportError:
    from .src.main import Main

_ERROR = 1
_SUCCESS = 0
_SKIPPED = 3
_SHOW_CONVERTED_IMAGE: bool = True
_CWD = os.path.dirname(os.path.abspath(__file__))
_BINARY_NAME = "MDI2TIF.EXE"
_DEBUG_ENABLED: bool = False
_SPLASH: bool = True

print(f"(mdi2img) module cwd = {_CWD}")

MI = Main(
    success=_SUCCESS,
    error=_ERROR,
    skipped=_SKIPPED,
    show=_SHOW_CONVERTED_IMAGE,
    cwd=_CWD,
    binary_name=_BINARY_NAME,
    debug=_DEBUG_ENABLED,
    splash=_SPLASH
)
MI.const.pdebug("Initialised MDI2IMG module", __name__, _CWD)
status = MI.main()
if isinstance(status, bool) is True:
    if status is True:
        sys.exit(MI.success)
    else:
        sys.exit(MI.error)
sys.exit(status)
