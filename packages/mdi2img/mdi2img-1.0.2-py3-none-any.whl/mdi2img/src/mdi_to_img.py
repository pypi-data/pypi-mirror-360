"""
    File in charge of linking the different elements of the program
"""

import tkinter as tk
from window_asset_tkinter import WindowAsset
from .viewer import ViewImage
from .img_to_tiff import MDIToTiff


class MDIToIMG:
    """ The class in charge of linking the different elements of the program """

    def __init__(self, parent_window: tk.Tk, success: int = 0, error: int = 1, width: int = 500, height: int = 400) -> None:
        # super(MDIToIMG, self).__init__()
        self.window_asset = WindowAsset()
        self.mdi_to_tiff = MDIToTiff(
            "MDI2TIF.EXE",
            success=success,
            error=error
        )
        self.view_image = ViewImage(
            parent_window=parent_window,
            width=width,
            height=height,
            success=success,
            error=error
        )

    # def test_mdi_to_img(self) -> None:
    #     """ Test the mdi to img """
    #     print("Testing mdi to img")
    #     print(f"window_asset = {dir(self.window_asset)}")
    #     print(f"view_image = {dir(self.view_image)}")

    # def main(self) -> None:
    #     """ The main function """
    #     self.test_mdi_to_img()
    #     self.window_asset.window_tools.unsorted.init_plain_window()
    #     self.window_asset.window_tools.unsorted.init_window(
    #         self.window_asset.window_tools.unsorted.init_plain_window(),
    #         "MDI to IMG",
    #         "black",
    #         500,
    #         500,
    #         0,
    #         0,
    #         False,
    #         False,
    #     )
    #     self.window_asset.window_tools.unsorted.load_image
