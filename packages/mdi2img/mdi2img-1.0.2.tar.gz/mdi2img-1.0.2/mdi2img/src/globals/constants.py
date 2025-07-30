"""
This module contains the Constants class, which is used to store global variables and methods that are used across different classes in the project.
It also provides utility functions for logging and error handling.
It is designed to be used as a singleton, ensuring that there is only one instance of the Constants class throughout the application.
"""
import os
import inspect
import platform
from typing import Union
from random import randint
from display_tty import Disp, TOML_CONF, LoggerColours
from . import logo as LOG

SUCCESS = 0
ERROR = 1
ERR = ERROR
SKIPPED = 3

SELECTED_LIST = LOG.__logo_ascii_art__
SPLASH_NAME = list(SELECTED_LIST)[randint(0, len(SELECTED_LIST) - 1)]
SPLASH = SELECTED_LIST[SPLASH_NAME]

__version__ = "1.0.0"
__author__ = "(c) Henry Letellier"

_CLASS_NAME = "Constants"

_CWD = os.path.dirname(os.path.abspath(__file__))


class Constants:
    """_summary_
    This is the class that will store general methods and variables that will be used over different classes.
    """

    def __init__(self, binary_name: str = "MDI2TIF.EXE", output_format: str = "default", cwd: str = _CWD, error: int = ERROR, success: int = SUCCESS, debug: bool = False) -> None:
        _func_name = inspect.currentframe().f_code.co_name
        _padding = "-" * 10
        # ---------------------------- Local global variables ----------------------------
        self.env = os.environ
        self.author = __author__
        self.debug = debug
        self.binary_name = binary_name
        self.in_directory = f"{os.getcwd()}/in"
        self.out_directory = f"{os.getcwd()}/out"
        self.out_format = output_format
        self.cwd = cwd
        self.success = success
        self.error = error
        # ---------------------------- Display debug object ----------------------------
        self.dttyi = Disp(
            toml_content=TOML_CONF,
            save_to_file=False,
            file_name="",
            file_descriptor=None,
            debug=self.debug,
            logger="mdi2img",
            success=self.success,
            error=self.error,
            log_warning_when_present=self.debug,
            log_errors_when_present=True,
        )
        self.level_success = 200
        self.dttyi.add_custom_level(
            level=self.level_success,
            name="SUCCESS",
            colour_text=LoggerColours.GREEN,
            colour_bg=LoggerColours.BLACK
        )
        self.pdebug(
            f"{_padding} Locating temporary folder {_padding}",
            _func_name
        )
        self.temporary_folder = self.get_temp_folder(self.env)
        self.temporary_img_folder = f"{self.temporary_folder}/mdi_to_img_temp"
        self.log_file_location = f"{self.temporary_folder}/mdi2tiff.log"
        self.pdebug(
            f"{_padding} Creating temporary folder if not present {_padding}",
            _func_name
        )
        self._create_temp_if_not_present()
        self.pdebug(
            f"{_padding} Searching for binary location {_padding}",
            _func_name
        )
        self.pdebug(
            f"Binary name: '{self.binary_name}'",
            _func_name
        )
        self.binary_path = self._find_mdi2tiff_binary(self.binary_name)
        self.pdebug(
            f"Binary path: '{self.binary_path}'",
            _func_name
        )
        # ---------------------------- Debug data ----------------------------
        # self.pdebug(
        #     f"{_padding} Displaying variables located in the Constants class {_padding}",
        #     _func_name
        # )
        # self.pdebug(f"self.env = {self.env}", _func_name)
        # self.pdebug(f"self.author = {self.author}", _func_name)
        # self.pdebug(f"self.debug = {self.debug}", _func_name)
        # self.pdebug(f"self.binary_name = {self.binary_name}", _func_name)
        # self.pdebug(f"self.in_directory = {self.in_directory}", _func_name)
        # self.pdebug(f"self.out_directory = {self.out_directory}", _func_name)
        # self.pdebug(f"self.out_format = {self.out_format}", _func_name)
        # self.pdebug(
        #     f"self.temporary_folder = {self.temporary_folder}",
        #     _func_name
        # )
        # self.pdebug(
        #     f"self.temporary_img_folder = {self.temporary_img_folder}",
        #     _func_name
        # )
        # self.pdebug(
        #     f"self.log_file_location = {self.log_file_location}", _func_name
        # )
        # self.pdebug(f"self.binary_path = {self.binary_path}", _func_name)

    @staticmethod
    def get_temp_folder(env: dict[str, str]) -> str:
        """_summary_
        Check the computer environement to see if the wished key is present.

        Returns:
            str: _description_: The value of the research.
        """
        if platform.system() != "Windows":
            return "/tmp"
        if "TEMP" in env:
            return env["TEMP"]
        if "TMP" in env:
            return env["TMP"]
        return os.getcwd()

    def _find_mdi2tiff_binary(self, binary_name: str = "MDI2TIF.EXE") -> Union[str, None]:
        """
        Search for the mdi2tiff binary in the module's directory.
        :param binary_name: The name of the binary to locate
        :return:
            str: Full path to the mdi2tiff binary if found, None otherwise.
        """
        _func_name = inspect.currentframe().f_code.co_name

        self.pdebug(f"Searching for binary: '{binary_name}'", _func_name)

        if self.cwd == "":
            current_script_directory = os.path.dirname(
                os.path.abspath(__file__)
            )
        else:
            current_script_directory = self.cwd

        self.pdebug(
            f"Current script directory: '{current_script_directory}'",
            _func_name
        )
        self.pdebug(
            f"Current working directory: '{self.cwd}'",
            _func_name
        )
        self.pdebug(
            f"Binary name: '{binary_name}'",
            _func_name
        )

        if isinstance(binary_name, str) is False or binary_name == "":
            msg = "Binary name is not a string or is empty."
            self.pcritical(msg, _func_name)
            return None

        binary_path = os.path.join(
            current_script_directory,
            "bin",
            binary_name
        )

        self.pdebug(f"Binary path: '{binary_path}'", _func_name)

        if os.path.exists(binary_path) is True:
            return binary_path
        return None

    def _create_temp_if_not_present(self) -> None:
        """_summary_
        Create the temporary folder if it does not exist.
        """
        _func_name = inspect.currentframe().f_code.co_name
        self.pdebug(
            f"Temporary export location: '{self.temporary_img_folder}'",
            _func_name
        )
        if os.path.exists(self.temporary_img_folder) is False:
            self.pinfo(
                "Temporary export location does not exist. Creating.",
                _func_name
            )
            try:
                os.makedirs(self.temporary_img_folder, exist_ok=True)
                msg = "Temporary export folder created in: "
                msg += f"'{self.temporary_img_folder}'."
                self.psuccess(msg, _func_name)
            except os.error as e:
                msg = "Error creating temporary export location ('"
                msg += f"{self.temporary_img_folder}'): {e}"
                self.pcritical(msg, _func_name)

    def update_debug(self, debug: bool) -> None:
        """_summary_
        Update the debug variable.

        Args:
            debug (bool): _description_: The new debug value.
        """
        self.debug = debug
        self.dttyi.update_disp_debug(debug)

    def perror(self, string: str = "", func_name: Union[str, None] = None, class_name: str = _CLASS_NAME) -> None:
        """_summary_
        This is a function that will output an error on the terminal.

        Args:
            string (str, optional): _description_. Defaults to "".
            func_name (Union[str, None], optional): _description_. Defaults to None.
            class_name (str, optional): _description_. Defaults to the value contained in _CLASS_NAME.
        """
        if isinstance(func_name, str) is False or func_name is None:
            _func_name = inspect.currentframe()
            if _func_name.f_back is not None:
                func_name = _func_name.f_back.f_code.co_name
            else:
                func_name = _func_name.f_code.co_name
        self.dttyi.log_error(string, f"{class_name}::{func_name}")

    def pwarning(self, string: str = "", func_name: Union[str, None] = None, class_name: str = _CLASS_NAME) -> None:
        """_summary_
        This is a function that will output a warning on the terminal.

        Args:
            string (str, optional): _description_. Defaults to "".
            func_name (Union[str, None], optional): _description_. Defaults to None.
            class_name (str, optional): _description_. Defaults to the value contained in _CLASS_NAME.
        """
        if isinstance(func_name, str) is False or func_name is None:
            _func_name = inspect.currentframe()
            if _func_name.f_back is not None:
                func_name = _func_name.f_back.f_code.co_name
            else:
                func_name = _func_name.f_code.co_name
        self.dttyi.log_warning(string, f"{class_name}::{func_name}")

    def pcritical(self, string: str = "", func_name: Union[str, None] = None, class_name: str = _CLASS_NAME) -> None:
        """_summary_
        This is a function that will output a critical error on the terminal.

        Args:
            string (str, optional): _description_. Defaults to "".
            func_name (Union[str, None], optional): _description_. Defaults to None.
            class_name (str, optional): _description_. Defaults to the value contained in _CLASS_NAME.
        """
        if isinstance(func_name, str) is False or func_name is None:
            _func_name = inspect.currentframe()
            if _func_name.f_back is not None:
                func_name = _func_name.f_back.f_code.co_name
            else:
                func_name = _func_name.f_code.co_name
        self.dttyi.log_critical(string, f"{class_name}::{func_name}")

    def psuccess(self, string: str = "", func_name: Union[str, None] = None, class_name: str = _CLASS_NAME) -> None:
        """_summary_
        This is a function that will output a success message on the terminal.

        Args:
            string (str, optional): _description_. Defaults to "".
            func_name (Union[str, None], optional): _description_. Defaults to None.
            class_name (str, optional): _description_. Defaults to the value contained in _CLASS_NAME.
        """
        if isinstance(func_name, str) is False or func_name is None:
            _func_name = inspect.currentframe()
            if _func_name.f_back is not None:
                func_name = _func_name.f_back.f_code.co_name
            else:
                func_name = _func_name.f_code.co_name
        self.dttyi.log_custom_level(
            self.level_success,
            string,
            f"{class_name}::{func_name}"
        )

    def pinfo(self, string: str = "", func_name: Union[str, None] = None, class_name: str = _CLASS_NAME) -> None:
        """_summary_
        This is a function that will output an information message on the terminal.

        Args:
            string (str, optional): _description_. Defaults to "".
            func_name (Union[str, None], optional): _description_. Defaults to None.
            class_name (str, optional): _description_. Defaults to the value contained in _CLASS_NAME.
        """
        if isinstance(func_name, str) is False or func_name is None:
            _func_name = inspect.currentframe()
            if _func_name.f_back is not None:
                func_name = _func_name.f_back.f_code.co_name
            else:
                func_name = _func_name.f_code.co_name
        self.dttyi.log_info(string, f"{class_name}::{func_name}")

    def pdebug(self, string: str = "", func_name: Union[str, None] = None, class_name: str = _CLASS_NAME) -> None:
        """_summary_
        This is a function that will output a debug message on the terminal.

        Args:
            string (str, optional): _description_. Defaults to "".
            func_name (Union[str, None], optional): _description_. Defaults to None.
            class_name (str, optional): _description_. Defaults to the value contained in _CLASS_NAME.
        """
        if isinstance(func_name, str) is False or func_name is None:
            _func_name = inspect.currentframe()
            if _func_name.f_back is not None:
                func_name = _func_name.f_back.f_code.co_name
            else:
                func_name = _func_name.f_code.co_name
        if self.debug is True:
            self.dttyi.log_debug(string, f"{class_name}::{func_name}")

    def err_item_not_found(self, directory: bool = True,  item_type: str = "input", path: str = '', critical: bool = False, additional_text: str = "") -> None:
        """_summary_
        This is a function that will output an error message when a directory is not found.

        Args:
            directory (bool, optional): _description_: Is the item a directory. Defaults to True.
            item_type (str, optional): _description_: The type of the item.
            path (str, optional): _description_: The path of the directory.
            critical (bool, optional): _description_ Is the message of critical importance. Defaults to True.
        """
        _func_name = inspect.currentframe().f_code.co_name
        dir_str = "directory"
        if directory is False:
            dir_str = "file"
        msg = f"The {item_type} {dir_str} ('{path}') was not found!"
        msg += f"{additional_text}"
        if critical is True:
            msg += "\n Aborting operation(s)!"
            self.pcritical(msg, _func_name)
        else:
            self.pwarning(msg, _func_name)

    def err_binary_path_not_found(self) -> None:
        """_summary_

        Args:
            critical (bool, optional): _description_ Is the message of critical importance. Defaults to True.
        """
        _func_name = inspect.currentframe().f_code.co_name
        msg = f"Binary path: '{self.binary_path}' was not found."
        msg += "\nAborting operations."
        self.pcritical(msg, _func_name)


TMP_IMG_FOLDER = Constants().temporary_img_folder
