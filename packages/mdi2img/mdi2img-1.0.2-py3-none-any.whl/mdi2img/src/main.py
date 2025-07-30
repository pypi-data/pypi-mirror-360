"""_summary_
    This is a file that will contain the code required to launch a pre-processor for the program
    This is also where input arguments will be managed
"""

import os
import sys
from typing import Tuple, List, Literal

from sys import argv

from .img_to_tiff import MDIToTiff
from .globals import constants as CONST
from .viewer import ViewImage
from .convert_to_any import AVAILABLE_FORMATS, AVAILABLE_FORMATS_HELP

DEBUG_RULES: Tuple[
    Literal['--debug'],
    Literal['-debug'],
    Literal['/debug'],
    Literal['--d'],
    Literal['-d'],
    Literal['/d']
] = (
    "--debug", "-debug", "/debug",
    "--d", "-d", "/d"
)

HELP_RULES: Tuple[
    Literal['--help'],
    Literal['--h'],
    Literal['--?'],
    Literal['-help'],
    Literal['-h'],
    Literal['-?'],
    Literal['/help'],
    Literal['/h'],
    Literal['/?']
] = (
    "--help", "--h", "--?",
    "-help", "-h", "-?",
    "/help", "/h", "/?"
)

VERSION_RULES: Tuple[
    Literal['--version'],
    Literal['-version'],
    Literal['/version'],
    Literal['--v'],
    Literal['-v'],
    Literal['/v']
] = (
    "--version", "-version", "/version",
    "--v", "-v", "/v"
)

NO_SHOW_RULES: Tuple[
    Literal['--no-show'],
    Literal['-no-show'],
    Literal['/no-show'],
    Literal['--noshow'],
    Literal['-noshow'],
    Literal['/noshow'],
    Literal['--ns'],
    Literal['-ns'],
    Literal['/ns'],
    Literal['--no_show'],
    Literal['-no_show'],
    Literal['/no_show']
] = (
    "--no-show", "-no-show", "/no-show",
    "--noshow", "-noshow", "/noshow",
    "--ns", "-ns", "/ns",
    "--no_show", "-no_show", "/no_show"
)

DESTINATION_RULES: Tuple[
    Literal['--destination'],
    Literal['-destination'],
    Literal['/destination'],
    Literal['--dest'],
    Literal['-dest'],
    Literal['/dest']
] = (
    "--destination", "-destination", "/destination",
    "--dest", "-dest", "/dest"
)

FORMAT_RULES: Tuple[
    Literal['--format'],
    Literal['-format'],
    Literal['/format'],
    Literal['--f'],
    Literal['-f'],
    Literal['/f']
] = (
    "--format", "-format", "/format",
    "--f", "-f", "/f"
)

WINDOW_WIDTH_RULES: Tuple[
    Literal['--window-width'],
    Literal['-window-width'],
    Literal['/window-width'],
    Literal['--ww'],
    Literal['-ww'],
    Literal['/ww']
] = (
    "--window-width", "-window-width", "/window-width",
    "--ww", "-ww", "/ww"
)

WINDOW_HEIGHT_RULES: Tuple[
    Literal['--window-height'],
    Literal['-window-height'],
    Literal['/window-height'],
    Literal['--wh'],
    Literal['-wh'],
    Literal['/wh']
] = (
    "--window-height", "-window-height", "/window-height",
    "--wh", "-wh", "/wh"
)

SYSTEM_VIEWER: Tuple[
    Literal['--system-viewer'],
    Literal['-system-viewer'],
    Literal['/system-viewer'],
    Literal['--sv'],
    Literal['-sv'],
    Literal['/sv']
] = (
    "--system-viewer", "-system-viewer", "/system-viewer",
    "--sv", "-sv", "/sv"
)

_CWD = os.path.dirname(os.path.abspath(__file__))

WINDOW_WIDTH = 500

WINDOW_HEIGHT = 400


class Main:
    """_summary_
    This is the main class of the program
    """

    def __init__(self, success: int = CONST.SUCCESS, error: int = CONST.ERROR, skipped: int = CONST.SKIPPED, show: bool = True, cwd: str = _CWD, binary_name: str = "MDI2TIF.EXE", debug: bool = False, splash: bool = True, window_width: int = WINDOW_WIDTH, window_height: int = WINDOW_HEIGHT) -> None:
        # -------------------------- Inherited values --------------------------
        self.cwd = cwd
        self.show = show
        self.error = error
        self.debug = debug
        self.success = success
        self.skipped = skipped
        self.binary_name = binary_name
        # ------------------- Check for a debug flag in argv -------------------
        for i in argv:
            if i.lower() in DEBUG_RULES:
                self.debug = True
                break
        # ------------------------ Argv pre-processing  ------------------------
        self.argv = argv[1:]
        self.argc = len(self.argv)
        # ----------------------------- Class name -----------------------------
        self.class_name = self.__class__.__name__
        # ------------------- Display the programs Boot logo -------------------
        self._display_splash_screen(splash)
        # ------------- Set basic variables required for the class -------------
        self.src = ""
        self.dest = ""
        self.available_formats = AVAILABLE_FORMATS
        self.dest_found = False
        self.output_format = "default"
        self.window_width = window_width
        self.window_height = window_height
        self.use_default_system_viewer = False
        # ------------------- Initialise the constants class -------------------
        self.const = CONST.Constants(
            self.binary_name,
            self.output_format,
            self.cwd,
            self.error,
            self.success,
            self.debug
        )
        # -------------- Check the arguments provided by the user --------------
        self._check_args()
        # ---- Check the destination variable before defaulting to fallback ----
        if self.dest_found is False:
            self.dest = self.const.temporary_img_folder
        # ------------------- Initialise the MDIToTiff class -------------------
        self.mdi_to_tiff_initialised: MDIToTiff = MDIToTiff(
            self.const,
            self.success,
            self.error,
            self.skipped
        )
        # --------------------- Initialise the viewer class ---------------------
        self.viewer_initialised: ViewImage = ViewImage(
            binary_name=self.const,
            parent_window=None,
            width=self.window_width,
            height=self.window_height,
            success=self.success,
            error=self.error,
            debug=self.debug,
            delay_init=True,
            use_default_system_viewer=self.use_default_system_viewer
        )
        # -------------------- End of class initialisation  --------------------

    def _display_splash_screen(self, display: bool = True) -> None:
        """_summary_
            This is the function that will display the splash screen if authorised to.

        Args:
            display (bool, optional): _description_: The boolean variable that controls the display of the splash screen. Defaults to True.
        """
        if display is True:
            if isinstance(CONST.SPLASH, list):
                for i in CONST.SPLASH:
                    print(i)
            else:
                print(CONST.SPLASH)
            print(f"Splash name: '{CONST.SPLASH_NAME}'")
        print("Welcome to Mdi2Img")

    def _sanitize_path(self, risky_path: str, check_presence: bool = True) -> Tuple[str, bool]:
        """_summary_

        Args:
            risky_path (str): _description_: The path to be sanitized.
            check_presence (bool, optional): _description_: Do a multi prong approche for checking the presence of the path. Defaults to True.
        Returns:
            str: _description_
        """
        cleaned_path = risky_path
        if risky_path.startswith("'") or risky_path.startswith('"'):
            cleaned_path = cleaned_path[1:]
            self.const.pdebug("Cleaning path: removing starting quote")
        if risky_path.endswith("'") or risky_path.endswith('"'):
            cleaned_path = cleaned_path[:-1]
            self.const.pdebug("Cleaning path: removing ending quote")
        if check_presence:
            if os.path.exists(cleaned_path) or os.path.isfile(cleaned_path) or os.path.isdir(cleaned_path):
                return [cleaned_path, True]
            cleaned_path2 = cleaned_path.replace("\\", "/")
            self.const.pdebug(
                f"cleaned_path2: {cleaned_path2}",
                class_name=self.class_name
            )
            if os.path.exists(cleaned_path2) or os.path.isfile(cleaned_path2) or os.path.isdir(cleaned_path2):
                self.const.pdebug(
                    f"cleaned_path is a path: {cleaned_path2}, is_path: True",
                    class_name=self.class_name
                )
                return [cleaned_path2, True]
            cleaned_path_stripped = cleaned_path2.strip()
            self.const.pdebug(
                f"cleaned_path_stripped: {cleaned_path_stripped}",
                class_name=self.class_name
            )
            if os.path.exists(cleaned_path_stripped) or os.path.isfile(cleaned_path_stripped) or os.path.isdir(cleaned_path_stripped):
                self.const.pdebug(
                    f"cleaned_path is a path: {cleaned_path}, is_path: True",
                    class_name=self.class_name
                )
                return [cleaned_path_stripped, True]
        return [cleaned_path, os.path.exists(cleaned_path)]

    def _is_a_valid_path_structure(self, unsure_path: str) -> bool:
        """_summary_
        Check if the path is a valid structure.
        This function will check if the path is a valid structure and if it is a valid path.
        It will return True if the path is a valid structure and False if it is not.

        Args:
            path (str): _description_: The path to be checked.
        Returns:
            bool: _description_: True if the path is a valid structure, False if it is not.
        """
        try:
            if os.path.isabs(unsure_path) or os.path.relpath(unsure_path):
                return True
        except ValueError:
            return False

    def _get_files_in_folder(self, folder: str, recursive: bool = True) -> List[str]:
        """_summary_
        Get all the files in a folder.

        Args:
            folder (str): _description_: The folder to be checked.
            recursive (bool, optional): _description_: Check if the function should be recursive. Defaults to True.

        Returns:
            List[str]: _description_: The list of files in the folder.
        """
        self.const.pdebug(
            f"Getting files in folder '{folder}'",
            class_name=self.class_name
        )
        if os.path.isdir(folder) is False:
            self.const.pdebug(
                f"The folder '{folder}' is not a directory.",
                class_name=self.class_name
            )
            return []
        if recursive is True:
            data: List[str] = []
            for i in os.listdir(folder):
                path = os.path.join(folder, i)
                self.const.pdebug(
                    f"Checking path '{path}'",
                    class_name=self.class_name
                )
                if os.path.isdir(path) is True:
                    self.const.pdebug(
                        f"Path '{path}' is a directory, checking recursively",
                        class_name=self.class_name
                    )
                    data += self._get_files_in_folder(path, recursive)
                else:
                    if i.split(".")[-1].lower() not in self.available_formats:
                        self.const.pdebug(
                            f"File '{path}' is not a valid format, skipping it.",
                            class_name=self.class_name
                        )
                        continue
                    self.const.pdebug(
                        f"Path '{path}' is a file, adding it to the list",
                        class_name=self.class_name
                    )
                    data.append(path)
            self.const.pdebug(
                f"Found {len(data)} files in folder '{folder}'",
                class_name=self.class_name
            )
            return data
        data: List[str] = []
        for i in os.listdir(folder):
            path = os.path.join(folder, i)
            self.const.pdebug(
                f"Checking path '{path}'",
                class_name=self.class_name
            )
            if os.path.isfile(path) is True:
                if i.split(".")[-1].lower() not in self.available_formats:
                    self.const.pdebug(
                        f"File '{path}' is not a valid format, skipping it.",
                        class_name=self.class_name
                    )
                    continue
                self.const.pdebug(
                    f"Path '{path}' is a file, adding it to the list",
                    class_name=self.class_name
                )
                data.append(path)
        self.const.pdebug(
            f"Found {len(data)} files in folder '{folder}'",
            class_name=self.class_name
        )
        return data

    def _check_output_format(self, output: str) -> str:
        """_summary_
        Check the output format provided by the user and return it if correct.

        Args:
            output (str): _description_: The output provided by the user.

        Returns:
            str: _description_: The format after the check.
        """
        data = output.lower()
        if data.startswith("'") or data.startswith('"'):
            data = data[1:]
            self.const.pdebug(
                "Cleaning format: removing starting quote",
                class_name=self.class_name
            )
        if data.endswith("'") or data.endswith('"'):
            data = data[:-1]
            self.const.pdebug(
                "Cleaning format: removing ending quote",
                class_name=self.class_name
            )
        if data in self.available_formats:
            return data
        self.const.pwarning(
            f"The format '{data}' is not supported, using the default format.",
            class_name=self.class_name
        )
        return self.output_format

    def _disp_version(self) -> None:
        """_summary_
        Display the version of the program
        """
        print(f"The version of this program is: {CONST.__version__}")

    def _help_section(self) -> None:
        """_summary_
        Display the help section of the program
        """
        print("USAGE:")
        msg = f"\t{argv[0]} <<-h>|<-v>|<SRC>> [DEST]|[--destination <DEST>] "
        msg += "[--debug] [--no-show] [--format=<format>] "
        msg += "[--window-width=<width>] [--window-height=<height>]"
        print(msg)
        print()
        print("KEEP IN MIND:")
        print("When exporting/viewing/saving images, the default output format is tiff.")
        print("Use the --format flag to change the export format.")
        msg = "When no destination is specified, "
        # msg += f"the default one is '{CONST.TMP_IMG_FOLDER}'"
        msg += f"the default one is '{self.const.temporary_img_folder}'"
        print(msg)
        print()
        print("ARGUMENTS:")
        print(
            "\tINFO: '<argument>' --> required, '[argument]' --> optional '|' --> one or the other"
        )
        print("\t<SRC>                             \tMust be either:")
        print("\t                                  \t  - a path to an mdi file")
        print("\t                                  \t  - a path to a folder containing mdi files")
        print("\t<-h>|<--help>                     \tDisplay this help section and exit.")
        print(
            "\t<-v>|<--version>                  \tDisplay the program's version and exit."
        )
        print("\t[DEST] | [--destination=<DEST>]   \tMust be either:")
        print("\t                                  \t  - the name of the output file")
        print("\t                                  \t  - the name of the output folder")
        print("\t[--debug|-d]                      \tThis option will display additional information about what the program is doing.")
        print("\t[--no-show|-ns]                   \tThis option will instruct the program not to display the images once they were converted")
        print("\t[--format=<format>]               \tThis option allows you to change the default output format (tiff)")
        print("\t[--window-width=<width>]          \tThis option allows you to change the default width of the window")
        print("\t[--window-height=<height>]        \tThis option allows you to change the default height of the window")
        print("\t[--system-viewer|-sv]             \tThis option will use the system viewer to display the images instead of the built-in viewer")
        print()
        print("ABOUT:")
        print(f"This program was created by {CONST.__author__}")
        self._disp_version()
        print()
        question = "Do you wish to see a list of the "
        question += f"{len(self.available_formats)} "
        question += "available formats [(y)es/(N)o]: "
        if input(question).lower() in ("y", "yes", "yas", "ye", "ys"):
            print("The available formats are:")
            index = 1
            for i in self.available_formats:
                print(f"\t{index}. '{i}': {AVAILABLE_FORMATS_HELP[i]}")
                index += 1

    def _check_args(self) -> None:
        """_summary_
        Check the arguments passed to the program
        """
        src_found = False
        self.dest_found = False
        skip_one = False
        if self.argc == 0:
            self._help_section()
            sys.exit(self.error)
        for index, item in enumerate(self.argv):
            self.const.pdebug(
                f"Checking argument '{item}'",
                class_name=self.class_name
            )
            arg = item.lower()
            arg_start = arg.split("=")[0] if "=" in arg else arg
            cleaned_item, is_path = self._sanitize_path(item, True)
            self.const.pdebug(
                f"Argument {item}, argument type = {type(item)}, cleaned_item: {cleaned_item}, is a path: {is_path}",
                class_name=self.class_name
            )
            if skip_one is True:
                skip_one = False
                self.const.pdebug(
                    f"Skipping argument '{item}'",
                    class_name=self.class_name
                )
                continue
            if arg in HELP_RULES:
                self._help_section()
                sys.exit(self.success)
            if arg in VERSION_RULES:
                self._disp_version()
                sys.exit(self.success)
            if is_path is True and src_found is False:
                self.src = cleaned_item
                src_found = True
                self.const.pdebug(
                    f"Source path found: {self.src}",
                    class_name=self.class_name
                )
                continue
            if (arg_start in DESTINATION_RULES and self.dest_found is False) or (is_path is True and src_found is True and self.dest_found is False):
                path = ""
                if "=" in item:
                    # Do not check for the presence of the path in the directory, because it is not supposed to exist yet
                    path = item.split("=")[1]
                    path, is_path = self._sanitize_path(path, True)
                    if self._is_a_valid_path_structure(path) is False:
                        self.const.pcritical(
                            f"Argument '{path}' is not a valid path structure, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                elif is_path is True:
                    # Do not check for the presence of the path in the directory, because it is not supposed to exist yet
                    path = cleaned_item
                    if self._is_a_valid_path_structure(path) is False:
                        self.const.pcritical(
                            f"Argument '{path}' is not a valid path structure, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                elif index + 1 < self.argc and self.argv[index + 1] != "" and self.argv[index + 1][0].startswith("-", 0) is False:
                    # Do not check for the presence of the path in the directory, because it is not supposed to exist yet
                    path = self.argv[index + 1]
                    path, is_path = self._sanitize_path(path, True)
                    if self._is_a_valid_path_structure(path) is False:
                        self.const.pcritical(
                            f"Argument '{path}' is not a valid path structure, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                    self.const.pdebug(
                        f"Argument '{self.argv[index + 1]}' found, using it as destination",
                        class_name=self.class_name
                    )
                    skip_one = True
                else:
                    self.const.pcritical(
                        f"No destination path provided for the {item} argument, skipping argument!",
                        class_name=self.class_name
                    )
                    continue
                self.dest = path
                self.dest_found = True
                self.const.pdebug(
                    f"Destination path found: {self.dest}",
                    class_name=self.class_name
                )
                continue
            if is_path is True and self.dest_found is True:
                self.const.pwarning(
                    f"Argument '{item}' was not expected, ignoring it.",
                    class_name=self.class_name
                )
                continue
            if arg in DEBUG_RULES:
                self.debug = True
                self.const.update_debug(self.debug)
                self.const.pdebug(
                    "Debug mode enabled.",
                    class_name=self.class_name
                )
                continue
            if arg in NO_SHOW_RULES:
                self.show = False
                self.const.pdebug(
                    "No show mode enabled.",
                    class_name=self.class_name
                )
                continue
            if arg_start in FORMAT_RULES:
                chosen_format = ""
                self.const.pdebug(
                    f"Argument '{arg}' found, checking for format",
                    class_name=self.class_name
                )
                if "=" in arg:
                    chosen_format = arg.split("=")[1]
                    self.const.pdebug(
                        f"Found format '{chosen_format}'",
                        class_name=self.class_name
                    )
                elif index + 1 < self.argc and self.argv[index + 1] != "" and self.argv[index + 1][0].startswith("-", 0) is False:
                    chosen_format = self.argv[index + 1]
                    skip_one = True
                    self.const.pdebug(
                        f"Found format '{chosen_format}'",
                        class_name=self.class_name
                    )
                else:
                    self.const.pcritical(
                        f"No format provided for the {arg} argument, aborting!",
                        class_name=self.class_name
                    )
                    continue
                self.const.pdebug(
                    f"Chosen format: {chosen_format}",
                    class_name=self.class_name
                )
                self.output_format = self._check_output_format(chosen_format)
                continue
            if arg_start in WINDOW_WIDTH_RULES:
                min_width = 20
                if "=" in arg:
                    node = arg.split("=")[1]
                    if node.isnumeric() is False:
                        self.const.pcritical(
                            f"Argument '{node}' is not a valid number, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                    node = int(node)
                    if node < min_width:
                        self.const.pcritical(
                            f"Argument '{node}' must be greater than {min_width}, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                    self.window_width = node
                    self.const.pdebug(
                        f"Window width set to {self.window_width}",
                        class_name=self.class_name
                    )
                elif index + 1 < self.argc and self.argv[index + 1] != "" and self.argv[index + 1][0].startswith("-", 0) is False:
                    node = self.argv[index + 1]
                    if node.isnumeric() is False:
                        self.const.pcritical(
                            f"Argument '{node}' is not a valid number, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                    node = int(node)
                    if node < min_width:
                        self.const.pcritical(
                            f"Argument '{node}' must be greater than {min_width}, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                    self.window_width = node
                    skip_one = True
                    self.const.pdebug(
                        f"Window width set to {self.window_width}",
                        class_name=self.class_name
                    )
                else:
                    self.const.pcritical(
                        f"No window width provided for the {arg} argument, skipping argument!",
                        class_name=self.class_name
                    )
                    continue
            if arg_start in WINDOW_HEIGHT_RULES:
                min_height = 20
                if "=" in arg:
                    node = arg.split("=")[1]
                    if node.isnumeric() is False:
                        self.const.pcritical(
                            f"Argument '{node}' is not a valid number, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                    node = int(node)
                    if node < min_height:
                        self.const.pcritical(
                            f"Argument '{node}' must be greater than {min_height}, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                    self.window_height = node
                    self.const.pdebug(
                        f"Window height set to {self.window_height}",
                        class_name=self.class_name
                    )
                elif index + 1 < self.argc and self.argv[index + 1] != "" and self.argv[index + 1][0].startswith("-", 0) is False:
                    node = self.argv[index + 1]
                    if node.isnumeric() is False:
                        self.const.pcritical(
                            f"Argument '{node}' is not a valid number, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                    node = int(node)
                    if node < min_height:
                        self.const.pcritical(
                            f"Argument '{node}' must be greater than {min_height}, skipping argument!",
                            class_name=self.class_name
                        )
                        continue
                    self.window_height = node
                    skip_one = True
                    self.const.pdebug(
                        f"Window width set to {self.window_height}",
                        class_name=self.class_name
                    )
                else:
                    self.const.pcritical(
                        f"No window width provided for the {arg} argument, skipping argument!",
                        class_name=self.class_name
                    )
                    continue
            if arg_start in SYSTEM_VIEWER:
                self.const.pdebug(
                    "System viewer mode enabled.",
                    class_name=self.class_name
                )
                self.use_default_system_viewer = True
                continue
            self.const.pdebug(
                f"Argument '{item}' was not expected, ignoring it.",
                class_name=self.class_name
            )
            continue
        if src_found is False:
            self.const.pcritical(
                "No source path provided, aborting!",
                class_name=self.class_name
            )
            sys.exit(self.error)
        self.const.pdebug(
            "Arguments parsed.",
            class_name=self.class_name
        )

    def main(self) -> int:
        """_summary_
        This is the main function of this class.

        Returns:
            int: _description_: The return status of the call
        """
        # Output values of given variables if debug is True
        if self.debug is True:
            self.const.update_debug(self.debug)
            for i in [
                ("self.src", self.src),
                ("self.dest", self.dest),
                ("self.dest_found", self.dest_found),
                ("self.debug", self.debug),
                ("self.show", self.show),
                ("self.output_format", self.output_format)
            ]:
                self.const.pdebug(
                    f"Variable '{i[0]}' = '{i[1]}'",
                    class_name=self.class_name
                )
        # If the destination path is empty, set the source path and update the extension.
        if len(self.dest) == 0 and os.path.isdir(self.src) is False:
            path = self.src
            if "." in path:
                cut_data = path.split(".")
                self.const.pdebug(
                    f"Cut data (step1): {cut_data}",
                    class_name=self.class_name
                )
                removed = cut_data.pop(-1)
                self.const.pdebug(
                    f"Cut data (step2): {cut_data}, popped info: {removed}",
                    class_name=self.class_name
                )
                cut_data.append("tiff")
                self.const.pdebug(
                    f"Cut data (step3): {cut_data}",
                    class_name=self.class_name
                )
                path = ".".join(cut_data)
                self.const.pdebug(
                    f"Cut data (step4): {path}",
                    class_name=self.class_name
                )
            else:
                path = f"{path}.tiff"
            self.dest = path
            self.const.pdebug(
                f"Destination path not provided, using '{self.dest}'",
                class_name=self.class_name
            )
        self.const.pdebug(f"dest: {self.dest}")
        self.const.pdebug(f"src: {self.src}")
        self.const.pdebug(f"output_format: {self.output_format}")
        # Check if the source is a folder
        if os.path.isdir(self.src) is True:
            self.const.pdebug(
                "The provided source path is a folder.",
                class_name=self.class_name
            )
            status = self.mdi_to_tiff_initialised.convert_all(
                self.src,
                self.dest,
                self.output_format
            )
            if status == self.error:
                return status
            # Displaying the converted image if the show flag is set to True
            self.const.pdebug(
                f"self.show = {self.show}",
                class_name=self.class_name
            )
            if self.show is True:
                self.const.pinfo(
                    "Gathering the converted images in the destination folder",
                    class_name=self.class_name
                )
                images = self._get_files_in_folder(self.dest, True)
                if len(images) == 0:
                    self.const.pdebug(
                        "No images found in the destination folder.",
                        class_name=self.class_name
                    )
                    return self.error
                self.const.pdebug(
                    f"Images found: {images}",
                    class_name=self.class_name
                )
                self.const.pdebug(
                    f"Window width: {self.window_width}",
                    class_name=self.class_name
                )
                self.const.pdebug(
                    f"Window height: {self.window_height}",
                    class_name=self.class_name
                )
                self.const.pinfo(
                    "Displaying the converted images",
                    class_name=self.class_name
                )
                self.viewer_initialised.default_to_system_viewer(
                    self.use_default_system_viewer)
                status = self.viewer_initialised.view(
                    images,
                    self.window_width,
                    self.window_height
                )
                return status
        # Check if the source is a file
        if os.path.isfile(self.src) is True:
            self.const.pdebug(
                "The provided source path is a file",
                class_name=self.class_name
            )
            self.const.pdebug(
                f"Source file: {self.src}",
                class_name=self.class_name
            )
            self.const.pdebug(
                f"Destination file: {self.dest}",
                class_name=self.class_name
            )
            self.const.pdebug(
                f"Output format: {self.output_format}",
                class_name=self.class_name
            )
            status = self.mdi_to_tiff_initialised.convert(
                self.src,
                self.dest,
                self.output_format
            )
            if status == self.error:
                return status
            # Displaying the converted image if the show flag is set to True
            self.const.pdebug(
                f"self.show = {self.show}",
                class_name=self.class_name
            )
            if self.show is True:
                self.const.pinfo(
                    "Displaying the converted image",
                    class_name=self.class_name
                )
                self.viewer_initialised.default_to_system_viewer(
                    self.use_default_system_viewer
                )
                status = self.viewer_initialised.view(
                    self.dest,
                    self.window_width,
                    self.window_height
                )
                return status
        # error output if the source is not a file or a folder
        self.const.pdebug(
            "The provided path does not correspond to a known type.",
            class_name=self.class_name
        )
        self.const.pcritical(
            f"The source path '{self.src}' does not exist or is neither a folder or a file\nAborting!",
            class_name=self.class_name
        )
        return self.error
