"""
File in charge of converting mdi files to tiff
This extension relies on the windows mdi2tiff program
"""

import os
import shutil
import platform
from typing import Union, List
from ..globals import constants as CONST
from ..convert_to_any import ChangeImageFormat


class MDIToTiff:
    """
    The class in charge of converting an mdi file to a tiff file
        :param success: The exit code of a successful conversion
        :param error: The exit code of a failed conversion
    """

    def __init__(self, binary_name: Union[str, CONST.Constants] = "", success: int = 0, error: int = 1, skipped: int = CONST.SKIPPED, output_format: str = "default", debug: bool = False) -> None:
        self.error = error
        self.success = success
        self.skipped = skipped
        self.debug = debug
        if callable(binary_name) is False:
            self.const = binary_name
        else:
            self.const = CONST.Constants(
                binary_name=binary_name,
                output_format=output_format,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                error=self.error,
                success=self.success,
                debug=self.debug
            )
        self.bin_path = self.const.binary_path
        # ------------------------ Store the class name ------------------------
        self.class_name = self.__class__.__name__
        # ------------------- Start Folder conversion stats --------------------
        self.session_active = False
        self.total_items = 0
        self.total_folders = 0
        self.total_nb_of_files = 0
        self.total_files_skipped = 0
        self.total_files_success = 0
        self.total_files_fails = 0
        self.global_status = self.success
        # -------------------- End Folder conversion stats ---------------------
        # ----------------------- Begin image conversion -----------------------
        self.cifi = ChangeImageFormat(
            constants=self.const,
            success=self.success,
            error=self.error
        )
        # ------------------------ End image conversion ------------------------

    def _reset_folder_conversion_stats_session(self) -> None:
        """_summary_
        Reset the folder conversion stats
        """
        self.total_items = 0
        self.total_folders = 0
        self.global_status = self.success
        self.session_active = False
        self.total_nb_of_files = 0
        self.total_files_fails = 0
        self.total_files_skipped = 0
        self.total_files_success = 0

    def _initialise_folder_conversion_stat_session(self, folder_content: List[str]) -> None:
        """_summary_
        Set the variables that can be set based on the contents of the folder

        Args:
            folder_content (List[str]): _description_: A list of the content of the input folder.
        """
        self._reset_folder_conversion_stats_session()
        self.total_items = len(folder_content)
        self.total_nb_of_files = self.total_items
        for i in folder_content:
            if os.path.isdir(i) is True:
                self.total_folders += 1
                self.total_nb_of_files -= 1
                continue
        self.session_active = True

    def _update_folder_conversion_stat_session(self, status: int = CONST.SUCCESS) -> None:
        """_summary_
        Update the conversion stats based on the status of the conversion

        Args:
            status (int, optional): _description_: The status of the conversion. Defaults to CONST.SUCCESS.
        """
        if status == self.success:
            self.total_files_success += 1
        elif status == self.skipped:
            self.total_files_skipped += 1
        else:
            self.total_files_fails += 1
            self.global_status = status

    def _display_folder_conversion_stat_session(self) -> None:
        """_summary_
        Display the conversion stats
        """
        self.const.pinfo(
            f"Total items: {self.total_items}",
            class_name=self.class_name
        )
        self.const.pinfo(
            f"Total folders: {self.total_folders}",
            class_name=self.class_name
        )
        self.const.pinfo(
            f"Total number of files: {self.total_nb_of_files}",
            class_name=self.class_name
        )
        self.const.pinfo(
            f"Total files skipped: {self.total_files_skipped}",
            class_name=self.class_name
        )
        self.const.pinfo(
            f"Total files success: {self.total_files_success}",
            class_name=self.class_name
        )
        self.const.pinfo(
            f"Total files fails: {self.total_files_fails}",
            class_name=self.class_name
        )
        if self.global_status == self.success:
            self.const.psuccess(
                "All files have been converted successfully.",
                class_name=self.class_name
            )
        else:
            self.const.perror(
                "Some files could not be converted.",
                class_name=self.class_name
            )

    def _is_bin_present(self, command: str) -> bool:
        """
        Check if a command is available using shutil.which (Python 3.3+)
        Works across all platforms.

        Args:
            command (str): The command to check

        Returns:
            bool: True if the command is available, False otherwise
        """
        return shutil.which(command) is not None

    def _is_dotnet_binary(self, binary_path: str) -> bool:
        """
        Detect if a binary is a .NET application by checking its headers.
        This is a simplified detection - a more robust implementation would 
        use libraries like 'pefile' for proper PE header analysis.

        Args:
            binary_path (str): Path to the binary

        Returns:
            bool: True if it appears to be a .NET application
        """
        try:
            # A very basic check - look for common .NET signatures in the file
            self.const.pdebug(
                f"Checking if binary is .NET: {binary_path}",
                class_name=self.class_name
            )
            with open(binary_path, 'rb') as f:
                content = f.read(8192)  # Read first 8KB

                self.const.pdebug(
                    f"Binary content read: {content[:50]}...",
                    class_name=self.class_name
                )

                # Looking for common .NET strings
                dotnet_signatures = [
                    b'mscoree.dll',
                    b'mscorlib',
                    b'.NET Framework',
                    b'System.Windows.Forms',
                    b'System.Drawing'
                ]

                for sig in dotnet_signatures:
                    if sig in content:
                        self.const.pdebug(
                            f"Found .NET signature: {sig}",
                            class_name=self.class_name
                        )
                        return True
            self.const.pdebug(
                "No .NET signature found in binary.",
                class_name=self.class_name
            )
            return False
        except Exception as e:
            self.const.pwarning(
                f"Error checking if binary is .NET: {e}",
                class_name=self.class_name
            )
            return False

    def _prepend_correct_linux_runner_if_required(self, binary_path: str) -> Union[str, None]:
        """
        Prepend the correct runner to the binary path if required.
        Detects and selects the appropriate interpreter for Windows executables on Linux/macOS.

        Args:
            binary_path (str): The path to the binary.

        Returns:
            str: The path to the binary with the correct runner, empty string on Windows,
                or None if no suitable runner is found.
        """
        # No runner needed on Windows
        if platform.system() == "Windows":
            self.const.pdebug(
                "No runner needed on Windows",
                class_name=self.class_name
            )
            return ""

        # For Linux or macOS systems
        if platform.system() == "Linux" or platform.system() == "Darwin":
            self.const.pdebug(
                f"Detected platform: {platform.system()}",
                class_name=self.class_name
            )
            # Check if the binary is a .NET application (better with mono)
            is_dotnet_app = binary_path.lower(
            ).endswith(
                '.exe'
            ) and self._is_dotnet_binary(binary_path)
            self.const.pdebug(
                f"Is .NET application: {is_dotnet_app}",
                class_name=self.class_name
            )

            # Dictionary of runners with their detection commands
            # Ordered by preference (will try in this order)
            runners = {}
            self.const.pdebug(
                "Checking for available runners",
                class_name=self.class_name
            )

            # For .NET applications, prioritize .NET-specific runners
            if is_dotnet_app:
                runners = {
                    "mono": "mono ",  # Best for .NET applications
                    "wine": "wine ",  # Fallback for .NET applications
                    "crossover": "crossover ",  # Commercial Wine variant
                    "proton": "proton run ",  # Valve's gaming-focused Wine fork
                }
            else:
                # For non-.NET applications, prioritize general Windows runners
                runners = {
                    "wine": "wine ",  # Best general compatibility
                    "crossover": "crossover ",  # Commercial Wine variant
                    "proton": "proton run ",  # Gaming-focused
                    "playonlinux": "playonlinux --run ",  # Wine frontend
                    "bottles": "bottles-cli run ",  # Modern Wine manager
                    "mono": "mono ",  # Last resort for non-.NET apps
                }

            self.const.pdebug(
                f"Runners available: {', '.join(runners.keys())}",
                class_name=self.class_name
            )

            # Check for each runner in order of preference
            for runner, command in runners.items():
                if self._is_bin_present(runner):
                    self.const.pinfo(
                        f"Using {runner} to run Windows executable",
                        class_name=self.class_name
                    )
                    return command

            # No suitable runner found
            self.const.perror(
                "No runner found for Linux or Mac. Please install wine, mono, crossover, or another Windows compatibility layer.",
                class_name=self.class_name
            )
            return None

        # Unsupported platform
        self.const.perror(
            f"Unsupported platform: {platform.system()}",
            class_name=self.class_name
        )
        return None

    def _run_conversion_steps(self, input_file: str, output_file: str, image_format: str) -> int:
        """_summary_
        This function is the one that will run the different conversion steps that are required in order to achieve the desired format.

        Args:
            input_file (str): _description_: The path to the input file.
            output_file (str): _description_: The path to the output file.
            image_format (str): _description_: The destination format of the image.

        Returns:
            int: _description_: The status of the execution.
        """
        self.const.pdebug(
            "Running conversion steps",
            class_name=self.class_name
        )
        if isinstance(output_file, list) is True:
            step1 = output_file[0]
            step2 = output_file[1]
        else:
            step1 = output_file
            step2 = None
        if image_format == "default":
            if step2 is not None:
                image_format = step2.split(".")[-1]
            else:
                image_format = step1.split(".")[-1]
        self.const.pdebug(
            f"Image format: {image_format}",
            class_name=self.class_name
        )
        self.const.pdebug(
            f"Step 1 (pending...): {step1}",
            class_name=self.class_name
        )
        self.const.pdebug(
            f"Step 2 (pending...): {step2}",
            class_name=self.class_name
        )
        # check binary permissions
        if os.access(self.bin_path, os.X_OK) is False:
            self.const.pwarning(
                f"Binary '{self.bin_path}' is not executable, granting permissions.",
                class_name=self.class_name
            )
            try:
                os.chmod(self.bin_path, 0o755)
                self.const.psuccess(
                    f"Permissions granted to '{self.bin_path}'",
                    class_name=self.class_name
                )
            except os.error as e:
                self.const.perror(
                    f"Error while granting permissions to '{self.bin_path}'",
                    class_name=self.class_name,
                    additional_text=f"Error: '{e}'"
                )
                return self.error
        prepended_bin_path = self._prepend_correct_linux_runner_if_required(
            self.bin_path
        )
        if prepended_bin_path is None:
            self.const.perror(
                "No suitable runner found for the binary.",
                class_name=self.class_name
            )
            return self.error
        if '"' in input_file:
            input_file = input_file.replace('"', '\\"')
        if '"' in step1:
            step1 = step1.replace('"', '\\"')
        if '"' in self.const.log_file_location:
            self.const.log_file_location = self.const.log_file_location.replace(
                '"', '\\"'
            )
        command = f"{prepended_bin_path}{self.bin_path} -source \"{input_file}\" -dest \"{step1}\" "
        command += f"-log \"{self.const.log_file_location}\""
        self.const.pdebug(
            f"Command: {command}",
            class_name=self.class_name
        )
        try:
            exit_code = os.system(command)
            self.const.pdebug(
                f"(os.system) Exit code: {exit_code}",
                class_name=self.class_name
            )
        except os.error as e:
            self.const.perror(
                f"Error while running the command: '{command}'",
                class_name=self.class_name,
                additional_text=f"Error: '{e}'"
            )
            exit_code = self.error
        if exit_code != self.success:
            return exit_code
        if step2 is not None:
            return self.cifi.to_desired_format(step1, step2, image_format)
        return exit_code

    def convert(self, input_file: str, output_file: Union[str, List[str]], img_format: str) -> int:
        """_summary_
        Convert an mdi file to a tiff file

        Args:
            input_file (str): _description_: The mdi file to convert
            output_file (Union[str, List[str, str]]): _description_: The tiff file to create

        Returns:
            int: _description_: The status of the convertion (success:int  or error:int)
        """
        self.const.pdebug("Converting file", class_name=self.class_name)
        if self.session_active is False and self.bin_path is None:
            self.const.err_binary_path_not_found()
            self.const.pdebug(
                "Binary path not found, aborting conversion.",
                class_name=self.class_name
            )
            return self.error
        self.const.pdebug(
            f"Input file: {input_file}",
            class_name=self.class_name
        )
        self.const.pdebug(
            f"Output file: {output_file}",
            class_name=self.class_name
        )
        self.const.pdebug(
            f"Image format: {img_format}",
            class_name=self.class_name
        )
        if os.path.isfile(input_file) is False:
            self.const.err_item_not_found(
                directory=False,
                item_type="input",
                path=input_file,
                critical=True
            )
            self.const.pdebug(
                f"'{input_file}' does not exist, aborting conversion.",
                class_name=self.class_name
            )
            return self.error
        if os.path.isfile(output_file) is True:
            self.const.pwarning(
                f"'{output_file}' already exists, skipping.",
                class_name=self.class_name
            )
            if self.session_active is True:
                return self.skipped
            return self.success
        self.const.pdebug(
            f"'{input_file}' exists, proceeding with conversion.",
            class_name=self.class_name
        )
        checked_output_file = self.cifi.check_output_file(
            output_file,
            img_format
        )
        self.const.pdebug(
            f"Checked output file: {checked_output_file}",
            class_name=self.class_name
        )
        exit_code = self._run_conversion_steps(
            input_file,
            checked_output_file,
            img_format
        )
        self.const.pdebug(
            f"Exit code: {exit_code}",
            class_name=self.class_name
        )
        if exit_code == self.success:
            if self.session_active is False:
                msg = f"{input_file} -> {output_file}: ok"
                self.const.psuccess(
                    msg,
                    class_name=self.class_name
                )
            return exit_code
        return self.error

    def convert_all(self, input_directory: str = "", output_directory: str = "", img_format: str = "") -> int:
        """_summary_
        Convert all mdi files in a directory to tiff files

        Args:
            input_directory (str, optional): _description_: The directory containing the mdi files to convert. Defaults to "".
            output_directory (str, optional): _description_: The directory where the tiff files will be created. Defaults to "".

        Returns:
            int: _description_: The status of the convertion (success:int  or error:int)
        """
        if input_directory == "":
            e = self.const.in_directory
            self.const.pwarning(
                f"No input directory was found, defaulting to: '{e}'",
                class_name=self.class_name
            )
            input_directory = e
        if output_directory == "":
            e = self.const.out_directory
            self.const.pwarning(
                f"No output directory was found, defaulting to: '{e}'",
                class_name=self.class_name
            )
            output_directory = e
        if self.bin_path is None:
            self.const.err_binary_path_not_found()
            return self.error
        if os.path.exists(input_directory) is False:
            self.const.err_item_not_found(True, "input", input_directory, True)
            return self.error
        if os.path.exists(output_directory) is False:
            try:
                os.makedirs(output_directory)
            except os.error as e:
                self.const.err_item_not_found(
                    True,
                    "output",
                    output_directory,
                    True,
                    additional_text=f"Error: '{e}'"
                )
                return self.error
        dir_content = os.listdir(input_directory)
        self._initialise_folder_conversion_stat_session(dir_content)
        for file in dir_content:
            if file.endswith(".mdi"):
                input_file = os.path.join(input_directory, file)
                if img_format == "default":
                    img_format = "tiff"
                output_file = os.path.join(
                    output_directory, file.replace(".mdi", f".{img_format}")
                )
                self.const.pinfo(
                    f"Converting '{input_file}' to '{output_file}'",
                    class_name=self.class_name
                )
                status = self.convert(input_file, output_file, img_format)
                self._update_folder_conversion_stat_session(status)
                if status == self.success:
                    msg = f"File '{input_file}' has been converted to "
                    msg += f"'{output_file}'."
                    self.const.psuccess(
                        msg,
                        class_name=self.class_name
                    )
                elif status == self.skipped:
                    msg = f"File '{input_file}' was skipped."
                    self.const.pinfo(
                        msg,
                        class_name=self.class_name
                    )
                else:
                    msg = f"File '{input_file}' could not be converted to "
                    msg += f"'{output_file}'"
                    self.const.perror(
                        msg,
                        class_name=self.class_name
                    )
            else:
                self.const.pwarning(
                    f"'{file}' is not an mdi file, skipping mdi conversion.",
                    class_name=self.class_name
                )
                src = os.path.join(input_directory, file)
                if img_format != "default" and file.endswith(f".{img_format}") is False:
                    temp = file.split(".")
                    self.const.pdebug(
                        f"Splitting file name (step 1): {temp}", class_name=self.class_name)
                    temp[-1] = img_format
                    self.const.pdebug(
                        f"Splitting file name (step 2): {temp}", class_name=self.class_name)
                    temp = ".".join(temp)
                    self.const.pdebug(
                        f"Splitting file name (step 3): {temp}", class_name=self.class_name)
                    dst = os.path.join(output_directory, temp)
                    self.const.pdebug(
                        f"Splitting file name (step 4): {dst}", class_name=self.class_name)
                else:
                    dst = os.path.join(output_directory, file)
                if img_format != file.split(".")[-1] and img_format != "default" and img_format in self.cifi.available_formats:
                    self.const.pinfo(
                        f"Converting '{file}' to '{img_format}'",
                        class_name=self.class_name
                    )
                    self.cifi.to_desired_format(
                        image=src,
                        output_name=dst,
                        img_format=img_format
                    )
                self.const.pinfo(
                    f"'{file}' is already in the desired format, copying without the second stage conversion.",
                    class_name=self.class_name
                )
                if src == dst or os.path.samefile(src, dst):
                    self.const.pwarning(
                        "Source and destination are the same, skipping copy.",
                        class_name=self.class_name
                    )
                    self._update_folder_conversion_stat_session(
                        self.skipped
                    )
                    continue
                self.const.pinfo(
                    f"Copying '{src}' to '{dst}'",
                    class_name=self.class_name
                )
                shutil.copy(
                    src,
                    dst
                )
        self._display_folder_conversion_stat_session()
        return self.global_status
