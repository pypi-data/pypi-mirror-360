"""
File in charge of displaying a converted image
"""

import os
import tkinter as tk
from typing import Union, Dict, List, Any
from platform import system
from window_asset_tkinter.window_tools import WindowTools as WT
from window_asset_tkinter.calculate_window_position import CalculateWindowPosition as CWP
from ..globals import constants as CONST


class ViewImage(WT):
    """
    The class in charge of displaying the image
    """

    def __init__(self, binary_name: Union[str, CONST.Constants] = "", parent_window: Union[tk.Tk, None] = None, width: int = 500, height: int = 400, success: int = 0, error: int = 1, delay_init: bool = False, debug: bool = False, use_default_system_viewer: bool = False) -> None:
        """
        The constructor of the class

        :param binary_name: The name of the binary to use, if not provided, it will use the default one
        :param parent_window: The parent window
        :param width: The width of the window
        :param height: The height of the window
        :param success: The success status code
        :param error: The error status code
        :param delay_init: If True, the window will not be initialised immediately
        :param debug: If True, the debug mode will be enabled
        :param use_default_system_viewer: If True, the viewer will use the system viewer by default
        """

        super(ViewImage, self).__init__()

        # The variable allowing us to toggle the verbosity of the output
        self.debug = debug
        self.class_name = self.__class__.__name__

        # Debug class instance
        if callable(binary_name) is False:
            self.const = binary_name
        else:
            self.const = CONST.Constants(
                binary_name=str(binary_name),
                output_format="default",
                cwd=os.path.dirname(os.path.abspath(__file__)),
                error=self.error,
                success=self.success,
                debug=self.debug
            )

        # Status codes
        self.success: int = success
        self.error: int = error
        self.error_message: str = "Error: Path does not exist"
        # Saving width and height of the window
        self.width: int = width
        self.height: int = height
        # Variable to inform if to delay the window initialisation or not
        self.delay_init: bool = delay_init
        # Creating parent window if it does not exist
        self.parent_window = None
        self._check_tkinter_parent_window(parent_window, delay_init=delay_init)
        # Gathering the dimensions of the user's screen to know where to place the window
        self.host_dimensions: Union[Dict[str, int], None] = None
        self._check_host_screen_dimensions(delay_init=delay_init)
        # Initialising the window position calculator
        self.cwp: Union[CWP, None] = None
        self._check_calculate_window_position(
            host_diemensions=self.host_dimensions,
            width=width,
            height=height,
            delay_init=delay_init
        )
        # Image tracking
        self._images_buffer: list = []
        self.image_data: list = []
        self.max_images: int = 0
        self.current_image: int = 0
        # Window position
        self.x_offset: int = 0
        self.y_offset: int = 0
        # GUI config
        self.bg: str = "white"
        self.fg: str = "black"
        # Title section
        self.title_label: tk.Label = tk.Label
        # image_viewer section
        self.image_viewer: tk.Label = tk.Label
        self.image_viewer_error: tk.Label = tk.Label
        self.has_been_forgotten: bool = False
        # button_prev section
        self.button_prev: tk.Button = tk.Button
        # button_next section
        self.button_next: tk.Button = tk.Button
        # button_open_in_viewer section
        self.button_open_in_viewer: tk.Button = tk.Button
        # The image counter
        self.image_count: tk.Label = tk.Label
        # Use system viewer
        self.use_system_viewer: bool = use_default_system_viewer

    def default_to_system_viewer(self, default_to_it: bool = True) -> None:
        """
        Set the viewer to use the system viewer by default: return: None
        """
        self.const.pdebug(
            "Setting the viewer to use the system viewer by default",
            class_name=self.class_name
        )
        if default_to_it is True:
            self.use_system_viewer = True
        else:
            self.use_system_viewer = False
        self.const.pdebug(
            "Viewer set to use the system viewer by default",
            class_name=self.class_name
        )

    def change_width(self, width: int) -> None:
        """
        Change the width of the window: param width: The new width of the window: return: None
        """
        self.const.pdebug(
            f"Changing width of the window to {width}",
            class_name=self.class_name
        )
        self.width = width
        if self.cwp is not None:
            self.cwp.change_width(width)
        self.const.pdebug(
            f"Width of the window changed to {self.width}",
            class_name=self.class_name
        )

    def change_height(self, height: int) -> None:
        """
        Change the height of the window: param height: The new height of the window: return: None
        """
        self.const.pdebug(
            f"Changing height of the window to {height}",
            class_name=self.class_name
        )
        self.height = height
        if self.cwp is not None:
            self.cwp.change_height(height)
        self.const.pdebug(
            f"Height of the window changed to {self.height}",
            class_name=self.class_name
        )

    def _check_tkinter_parent_window(self, parent_window: Union[tk.Tk, None] = None, delay_init: bool = False) -> None:
        """
        Check if the parent window is a tkinter window: return: None
        """
        self.const.pdebug(
            f"Checking if the parent window is a tkinter window: {parent_window}",
            class_name=self.class_name
        )
        if parent_window is None:
            if delay_init is True:
                self.parent_window = None
            else:
                self.parent_window = self._create_parent_window()
        else:
            self.parent_window = parent_window
        self.const.pdebug(
            f"Parent window set to: {self.parent_window}",
            class_name=self.class_name
        )

    def _check_host_screen_dimensions(self, delay_init: bool = False) -> None:
        """
        Check if the host screen dimensions are set: return: None
        """
        self.const.pdebug(
            f"Checking if the host screen dimensions are set: {self.host_dimensions}",
            class_name=self.class_name
        )
        if self.host_dimensions is None:
            if delay_init is True:
                self.host_dimensions = None
                return
            if self.parent_window is None:
                self.parent_window = self._create_parent_window()
            self.host_dimensions = self.get_current_host_screen_dimensions(
                self.parent_window
            )
        self.const.pdebug(
            f"Host screen dimensions set to: {self.host_dimensions}",
            class_name=self.class_name
        )

    def _check_calculate_window_position(self, host_diemensions: dict, width: int, height: int, delay_init: bool = False) -> None:
        """
        Check if the calculate window position is set: return: None
        """
        self.const.pdebug(
            f"Checking if the calculate window position is set: {self.cwp}",
            class_name=self.class_name
        )
        if self.cwp is None:
            if delay_init is True:
                self.cwp = None
                return
            if host_diemensions is None:
                self.host_dimensions = self.get_current_host_screen_dimensions(
                    self.parent_window
                )
            if "width" not in host_diemensions or "height" not in host_diemensions:
                return
            self.cwp = CWP(
                host_diemensions["width"],
                host_diemensions["height"],
                width,
                height
            )
        self.const.pdebug(
            f"Calculate window position set to: {self.cwp}",
            class_name=self.class_name
        )

    def _create_parent_window(self) -> tk.Tk:
        """
        This is the function in charge of initialising the base window that will be used to render the rest of the software.

        Create the parent window: return: The parent window
        """
        self.const.pdebug(
            "Creating the parent window",
            class_name=self.class_name
        )
        window = tk.Tk()
        window.withdraw()
        self.const.pdebug(
            "Parent window created",
            class_name=self.class_name
        )
        return window

    def _load_image(self, image_path_src: str, width: int, height: int) -> dict:
        """
        Load the image into memory: param image_path: The path to the image to load: return: The image node

        raw_content:
            * "img": < image_instance: obj >
            * "width": < width: int >
            * "height": < height: int >
            * "path": < image_path: str >
            * "name": < image_name: str >
        when error:
            * "name": < the_name: str >
            * "error": < the_error: str >
        """
        self.const.pdebug(
            f"Loading image from path: {image_path_src}",
            class_name=self.class_name
        )
        if os.path.exists(image_path_src) is False:
            path_message = {
                "name": image_path_src,
                "error": self.error_message
            }
            self._images_buffer.append(self.error_message)
            self.image_data.append(path_message)
            return path_message
        data = self.load_image(
            image_path=image_path_src,
            width=width,
            height=height
        )
        if "img" in data:
            current_name = image_path_src.replace("\\", "/")
            current_name = current_name.split("/")[-1]
            self._images_buffer.append(data["img"])
            node = {
                "img": data["img"],
                "width": width,
                "height": height,
                "path": image_path_src,
                "name": current_name
            }
            self.image_data.append(node)
            return node
        node = {
            "name": image_path_src,
            "error": data["err_message"]
        }
        self._images_buffer.append(data["err_message"])
        self.image_data.append(node)
        self.const.pdebug(
            f"Error loading image from path: {image_path_src}",
            class_name=self.class_name
        )
        return node

    def _load_images(self, image_paths: list[str], width: int, height: int) -> None:
        """
        Load multiple images into memory: param image_paths: The paths to the images to load: return: None
        """
        self.const.pdebug(
            f"Loading multiple images from paths: {image_paths}",
            class_name=self.class_name
        )
        for image_index, image_item in enumerate(image_paths):
            self._load_image(image_item, width, height)
            self.max_images = image_index
        self.const.pdebug(
            f"Loaded {self.max_images + 1} images",
            class_name=self.class_name
        )

    def _update_current_image_displayed(self) -> None:
        """
        Update the image displayed
        """
        self.const.pdebug(
            f"Updating the current image displayed: {self.current_image}",
            class_name=self.class_name
        )
        if len(self.image_data) > 0 and self.current_image >= len(self.image_data):
            self.current_image = 0
        if isinstance(self._images_buffer[self.current_image], str) is True:
            self.image_viewer.pack_forget()
            self.button_open_in_viewer.config(state=tk.DISABLED)
            self.image_viewer_error.config(
                text=self._images_buffer[self.current_image]
            )
            self.image_viewer_error.pack()
            self.has_been_forgotten = True
        else:
            if self.has_been_forgotten is True:
                self.image_viewer_error.pack_forget()
                self.image_viewer.pack()
                self.has_been_forgotten = False
            self.image_viewer.configure(
                image=self._images_buffer[self.current_image]
            )
            self.button_open_in_viewer.config(state=tk.NORMAL)
        self.const.pdebug(
            f"Current image displayed updated: {self.current_image}",
            class_name=self.class_name
        )

    def _update_current_image_index(self) -> None:
        """
        Update the index displayed of the current image
        """
        self.const.pdebug(
            f"Updating the current image index: {self.current_image}",
            class_name=self.class_name
        )
        self.image_count.config(
            text=f"Image {self.current_image + 1}/{self.max_images + 1}"
        )
        self.const.pdebug(
            f"Current image index updated: {self.current_image}",
            class_name=self.class_name
        )

    def _update_current_image_title(self) -> None:
        """
        Update the title of the current image
        """
        self.const.pdebug(
            f"Updating the current image title: {self.current_image}",
            class_name=self.class_name
        )
        self.title_label.config(
            text=self.image_data[self.current_image]["name"]
        )
        self.const.pdebug(
            f"Current image title updated: {self.image_data[self.current_image]['name']}",
            class_name=self.class_name
        )

    def _previous_image(self, *args) -> None:
        """
        Display the previous image and it's name
        :return: None
        """
        self.const.pdebug(
            f"Displaying the previous image: {self.current_image}",
            class_name=self.class_name
        )
        if self.max_images == 0:
            self.image_viewer.config(text="No images to display !")
            return
        if self.current_image > 0:
            self.current_image -= 1
        else:
            self.current_image = self.max_images
        self._update_current_image_displayed()
        self._update_current_image_title()
        self._update_current_image_index()
        self.const.pdebug(
            f"Previous image displayed: {self.current_image}",
            class_name=self.class_name
        )

    def _next_image(self, *args) -> None:
        """
        Display the next image and it's name
        :return: None
        """
        self.const.pdebug(
            f"Displaying the next image: {self.current_image}",
            class_name=self.class_name
        )
        if self.max_images == 0:
            self.image_viewer.config(text="No images to display !")
            return
        if self.current_image < self.max_images:
            self.current_image += 1
        else:
            self.current_image = 0
        self._update_current_image_displayed()
        self._update_current_image_title()
        self._update_current_image_index()
        self.const.pdebug(
            f"Displayed the next image: {self.current_image}",
            class_name=self.class_name
        )

    def hl_swap(self, item1: Any, item2: Any) -> list[Any, Any]:
        """
        Swap the values of two items
        :param item1: The first item
        :param item2: The second item
        :return: The items with their values swapped
        """
        self.const.pdebug(
            f"Swapping items: {item1} and {item2}",
            class_name=self.class_name
        )
        return [item2, item1]

    def _open_in_system_viewer(self, image_file_path: str = "") -> None:
        """
        Open the current image in the system viewer
        :return: None
        """
        self.const.pdebug(
            f"Opening the current image in the system viewer: {image_file_path}",
            class_name=self.class_name
        )
        if system() == "Windows":
            os.system(f"start \"\" \"{image_file_path}\"")
        elif system() == "Linux":
            os.system(f"xdg-open \"{image_file_path}\"")
        elif system() == "Darwin":
            os.system(f"open \"{image_file_path}\"")
        self.const.pdebug(
            f"Opened the current image in the system viewer: {image_file_path}",
            class_name=self.class_name
        )

    def _open_in_system_viewer_tk_rebind(self, *args) -> None:
        """
        Open the current image in the system viewer
        :return: None
        """
        self.const.pdebug(
            f"Opening the current image in the system viewer: {self.current_image}",
            class_name=self.class_name
        )
        current_image = self.current_image
        if self.current_image > self.max_images:
            current_image = 0
        if self.use_system_viewer is True:
            self._open_in_system_viewer(self.image_data[current_image]['path'])
        else:
            self.const.pdebug(
                "System viewer is not enabled, skipping opening in system viewer",
                class_name=self.class_name
            )

    def view(self, image_paths: list[str] | str, width: int = 0, height: int = 0) -> int:
        """
        Display an image
        :param image_path: The path to the image to display
        :return: The status of the display (success:int  or error:int)
        """
        self.const.pdebug(
            f"Displaying image(s): {image_paths}",
            class_name=self.class_name
        )
        if self.use_system_viewer is True:
            if isinstance(image_paths, (str, List)) is False:
                self.const.pdebug(
                    "System viewer is enabled, but the image_paths is not a string or list, skipping opening in system viewer",
                    class_name=self.class_name
                )
                return self.error
            if isinstance(image_paths, str) is True:
                image_paths = [image_paths]
            for i in image_paths:
                if isinstance(i, str) is True and os.path.exists(i) is True:
                    self.const.pdebug(
                        f"Opening image '{i}' in the system viewer",
                        class_name=self.class_name
                    )
                    self._open_in_system_viewer(i)
                else:
                    self.const.pdebug(
                        f"Path '{i}' does not exist, skipping it.",
                        class_name=self.class_name
                    )
            self.const.pdebug(
                "Opened images in the system viewer",
                class_name=self.class_name
            )
            return self.success
        button_width = 10
        object_height = 135
        self._check_tkinter_parent_window(None, False)
        self._check_host_screen_dimensions(False)
        self._check_calculate_window_position(
            self.host_dimensions,
            width,
            height,
            False
        )
        if width < 1:
            width = self.width - (button_width*2)
        else:
            width -= button_width*2
        if height < 1:
            height = self.height

        if width >= self.width:
            width = self.hl_swap(width, self.width)
            self.width = width[-1]+1
            width = width[0]
        if height >= self.height:
            height = self.hl_swap(height, self.height)
            self.height = height[-1]+1
            height = height[0]

        if isinstance(image_paths, str) is True:
            self._load_image(image_paths, width, height)
        elif isinstance(image_paths, list) is True:
            self._load_images(image_paths, width, height)
        else:
            return self.error
        window_coord = self.cwp.calculate_center()
        child_window = self.init_plain_window(self.parent_window)
        self.init_window(
            child_window,
            title="MDI viewer",
            bkg="white",
            width=self.width + self.x_offset,
            height=self.height + self.y_offset+object_height,
            position_x=window_coord[0],
            position_y=window_coord[1],
            fullscreen=False,
            resizable=True
        )
        title_frame = self.add_frame(
            child_window,
            borderwidth=0,
            relief=tk.FLAT,
            bkg="blue" if self.debug else self.bg,
            width=self.width,
            height=2,
            position_x=0,
            position_y=0,
            side=tk.TOP,
            fill=tk.X,
            anchor=tk.CENTER
        )
        image_frame = self.add_frame(
            child_window,
            borderwidth=0,
            relief=tk.FLAT,
            bkg="orange" if self.debug else self.bg,
            width=self.width,
            height=self.height - self.y_offset,
            position_x=0,
            position_y=0,
            side=tk.TOP,
            fill=tk.X,
            anchor=tk.CENTER
        )
        footer_frame = self.add_frame(
            child_window,
            borderwidth=0,
            relief=tk.FLAT,
            bkg="cyan" if self.debug else self.bg,
            width=self.width,
            height=2,
            position_x=0,
            position_y=0,
            side=tk.BOTTOM,
            fill=tk.X,
            anchor=tk.CENTER
        )
        button_frame = self.add_frame(
            child_window,
            borderwidth=0,
            relief=tk.FLAT,
            bkg="purple" if self.debug else self.bg,
            width=self.width,
            height=self.height - self.y_offset,
            position_x=0,
            position_y=0,
            side=tk.BOTTOM,
            fill=tk.NONE,
            anchor=tk.CENTER
        )

        button_prev_frame = self.add_frame(
            button_frame,
            borderwidth=0,
            relief=tk.FLAT,
            bkg="green" if self.debug else self.bg,
            width=self.width,
            height=self.height - self.y_offset,
            position_x=0,
            position_y=0,
            side=tk.LEFT,
            fill=tk.NONE,
            anchor=tk.CENTER
        )
        image_viewer_frame = self.add_frame(
            image_frame,
            borderwidth=0,
            relief=tk.FLAT,
            bkg="yellow" if self.debug else self.bg,
            width=self.width,
            height=self.height - self.y_offset,
            position_x=0,
            position_y=0,
            side=tk.LEFT,
            fill=tk.NONE,
            anchor=tk.CENTER
        )
        button_next_frame = self.add_frame(
            button_frame,
            borderwidth=0,
            relief=tk.FLAT,
            bkg="red" if self.debug else self.bg,
            width=self.width,
            height=self.height - self.y_offset,
            position_x=0,
            position_y=0,
            side=tk.LEFT,
            fill=tk.NONE,
            anchor=tk.CENTER
        )
        self.title_label = self.add_label(
            title_frame,
            text="MDI Viewer",
            bkg=self.bg,
            fg=self.fg,
            width=self.width,
            height=2,
            position_x=0,
            position_y=0,
            side=tk.TOP,
            fill=tk.X,
            anchor=tk.CENTER
        )
        self.image_viewer = self.add_label(
            image_viewer_frame,
            text="",
            bkg=self.bg,
            fg=self.fg,
            width=width,
            height=height - self.y_offset,
            position_x=20,
            position_y=0,
            side=tk.TOP,
            fill=tk.NONE,
            anchor=tk.CENTER
        )
        self.image_viewer_error = self.add_label(
            image_viewer_frame,
            text="",
            bkg=self.bg,
            fg=self.fg,
            width=width,
            height=2,
            position_x=20,
            position_y=0,
            side=tk.TOP,
            fill=tk.NONE,
            anchor=tk.CENTER
        )
        self.button_prev = self.add_button(
            button_prev_frame,
            text="Previous",
            fg=self.fg,
            bkg=self.bg,
            side=tk.TOP,
            command=self._previous_image,
            width=button_width,
            height=1,
            position_x=0,
            position_y=0,
            anchor=tk.CENTER,
            fill=tk.NONE
        )
        self.button_next = self.add_button(
            button_next_frame,
            text="Next",
            fg=self.fg,
            bkg=self.bg,
            side=tk.LEFT,
            command=self._next_image,
            width=button_width,
            height=1,
            position_x=0,
            position_y=0,
            anchor=tk.CENTER,
            fill=tk.NONE
        )
        self.button_open_in_viewer = self.add_button(
            button_next_frame,
            text="Open in system viewer",
            fg=self.fg,
            bkg=self.bg,
            side=tk.LEFT,
            command=self._open_in_system_viewer_tk_rebind,
            width=button_width*2,
            height=1,
            position_x=0,
            position_y=0,
            anchor=tk.CENTER,
            fill=tk.NONE
        )
        self.image_count = self.add_label(
            footer_frame,
            text=f"Image {self.current_image + 1}/{self.max_images + 1}",
            bkg=self.bg,
            fg=self.fg,
            width=self.width - (button_width*2),
            height=2,
            position_x=0,
            position_y=0,
            side=tk.TOP,
            fill=tk.X,
            anchor=tk.CENTER
        )
        self.add_watermark(
            window=footer_frame,
            side=tk.RIGHT,
            anchor=tk.E,
            bkg=self.bg,
            fg=self.fg
        )
        self._previous_image()
        self._next_image()
        child_window.wait_window()
        self.const.pdebug(
            f"Ran the main function (called view) of the {self.class_name} class",
            class_name=self.class_name
        )
        return True


if __name__ == "__main__":
    import sys
    ERROR = 1
    SUCCESS = 0
    WINDOW_WIDTH = 500
    WINDOW_HEIGHT = 400
    if (len(sys.argv) == 2 and sys.argv[1] in ("--help", "--h", "--?", "-h", "-?", "-help", "/?", "/h", "/help")):
        print(f"Usage: python3 {sys.argv[0]} <image_directory_path>")
        sys.exit(0)

    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <image_directory_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    if os.path.isdir(sys.argv[1]) is False:
        image_path = "../../sample_images"
        print(
            f"Error: '{sys.argv[1]}' is not a directory, defaulting to: {image_path}"
        )
        if os.path.isdir(image_path) is False:
            print(f"Error: default path '{image_path}' is not a directory")
            sys.exit(1)
    VII = ViewImage(
        binary_name="ee",
        parent_window=None,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        success=SUCCESS,
        error=ERROR
    )
    ressources = []
    if os.path.exists(image_path) is True:
        images = os.listdir(image_path)
        for index, item in enumerate(images):
            ressources.append(os.path.join(image_path, item))
        ressources.append("Not a path")
    VII.view(
        ressources,
        WINDOW_WIDTH,
        WINDOW_HEIGHT
    )
