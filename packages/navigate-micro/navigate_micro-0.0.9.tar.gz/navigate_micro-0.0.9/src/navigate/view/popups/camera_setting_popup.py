# Copyright (c) 2021-2024  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only
# (subject to the limitations in the disclaimer below)
# provided that the following conditions are met:

#      * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.

#      * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.

#      * Neither the name of the copyright holders nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.

# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Standard Library Imports
import tkinter as tk

# Third Party Imports

# Local Imports
from navigate.view.custom_widgets.popup import PopUp
from navigate.view.main_window_content.camera_tab import CameraSettingsTab

# p = __name__.split(".")[1]
# logger = logging.getLogger(p)


class CameraSettingPopup:
    """Popup window for camera setting."""

    def __init__(self, root, microscope_name, *args, **kwargs):
        """Initialize the CameraSettingPopup class.

        Parameters
        ----------
        root : tkinter.Tk
            Root window of the application.
        microscope_name : str
            Name of the microscope.
        args : list
            List of arguments.
        kwargs : dict
            Dictionary of keyword arguments.
        """
        # Creating popup window with this name and size/placement, PopUp is a
        # Toplevel window
        #: PopUp: Popup window for the camera view.
        self.popup = PopUp(
            root,
            f"{microscope_name} Camera Setting",
            "+320+180",
            top=False,
            transient=False,
        )
        self.popup.resizable(tk.TRUE, tk.TRUE)

        # Storing the content frame of the popup, this will be the parent of
        # the widgets
        content_frame = self.popup.get_frame()
        content_frame.columnconfigure(0, pad=5)
        content_frame.columnconfigure(1, pad=5)
        content_frame.rowconfigure(0, pad=5)
        content_frame.rowconfigure(1, pad=5)
        content_frame.rowconfigure(2, pad=5)

        # Formatting
        tk.Grid.columnconfigure(content_frame, "all", weight=1)
        tk.Grid.rowconfigure(content_frame, "all", weight=1)

        #: dict: Dictionary of all the input widgets.
        self.inputs = {}
        #: dict: Dictionary of all the buttons.
        self.buttons = {}

        # Camera setting tab.
        self.camera_setting = CameraSettingsTab(content_frame)
        self.camera_setting.is_popup = True
        self.camera_setting.is_docked = False
        self.camera_setting.grid(row=0, column=0, sticky=tk.NSEW)

    # Getters
    def get_variables(self):
        """Get the variables tied to the widgets.

        This function returns a dictionary of all the variables that are tied to each
        widget name.

        The key is the widget name, value is the variable associated.

        Returns
        -------
        dict
            Dictionary of all the variables that are tied to each widget name.
        """
        variables = {}
        for key, widget in self.inputs.items():
            variables[key] = widget.get_variable()
        return variables

    def get_widgets(self):
        """Get the dictionary that holds the input widgets.

        This function returns the dictionary that holds the input widgets.
        The key is the widget name, value is the LabelInput class that has all the data.

        Returns
        -------
        dict
            Dictionary that holds the input widgets.
        """
        return self.inputs

    def get_buttons(self):
        """Get the dictionary that holds the buttons.

        This function returns the dictionary that holds the buttons.
        The key is the button name, value is the button.

        Returns
        -------
        dict
            Dictionary that holds the buttons.
        """
        return self.buttons
