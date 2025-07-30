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
from tkinter import NSEW, NW, ttk
import tkinter
import logging

# Third Party Imports

# Local Imports
from navigate.view.custom_widgets.popup import PopUp

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class ilastik_setting_popup:
    """Popup window for setting up ilastik segmentation settings."""

    def __init__(self, root, *args, **kwargs):
        """Initialize the popup window

        Parameters
        ----------
        root : tkinter.Tk
            Root window
        *args :
            Variable length argument list
        **kwargs :
            Arbitrary keyword arguments
        """

        # Creating popup window with this name and size/placement, PopUp is a
        #: PopUp: PopUp window class
        self.popup = PopUp(
            root, "Ilastik Settings", "+320+180", top=False, transient=True
        )

        # Creating content frame
        content_frame = self.popup.get_frame()

        #: tkinter.StringVar: Variable for project name
        self.project_name_var = tkinter.StringVar(
            value="Please select an ilastik pixelclassification project file!"
        )

        project_name_entry = ttk.Entry(
            content_frame,
            textvariable=self.project_name_var,
            width=50,
            state="readonly",
        )
        project_name_entry.grid(row=1, column=0, pady=(10, 10), padx=(0, 10))
        #: ttk.Button: Button for loading ilastik project
        self.load_project_btn = ttk.Button(
            content_frame, text="Load Ilastik Project", width=30
        )
        self.load_project_btn.grid(row=1, column=1, pady=(10, 10), padx=(0, 10))

        tkinter.Label(content_frame, text="Select all target labels:").grid(
            row=2, sticky=NW
        )
        #: ttk.Frame: Frame for labels
        self.label_frame = ttk.Frame(content_frame, padding="3 3 12 12")
        self.label_frame.grid(row=3, columnspan=2, sticky=NSEW)
        default_colors = ["red", "#0082c8", "#ffe119"]
        for i in range(3):
            label_widget = ttk.Checkbutton(self.label_frame, text="Label" + str(i + 1))
            label_widget.grid(
                row=1 + i, column=0, pady=(0, 10), padx=(20, 5), sticky="W"
            )
            color_block = tkinter.Label(
                self.label_frame, background=default_colors[i], width=3, height=1
            )
            color_block.grid(row=1 + i, column=1, pady=(0, 10), padx=(0, 10))

        # segmentation usage
        tkinter.Label(content_frame, text="Choose the way to use segmentation:").grid(
            row=4, sticky=NW
        )
        #: tkinter.Checkbutton: Checkbutton for showing segmentation
        self.show_on_gui = tkinter.Checkbutton(content_frame, text="Show Segmentation")
        self.show_on_gui.grid(row=5, column=0, padx=(20, 0), pady=(10, 20), sticky="W")

        #: tkinter.Checkbutton: Checkbutton for marking position
        self.mark_position = tkinter.Checkbutton(content_frame, text="Mark Position")
        self.mark_position.grid(row=5, column=1, padx=(0, 0), pady=(10, 20), sticky="W")

        #: ttk.Button: Button for confirming setting
        self.confirm_btn = ttk.Button(content_frame, text="Confirm Setting", width=30)
        self.confirm_btn.grid(row=7, column=1, sticky="SE", padx=(0, 10), pady=(0, 10))

    def get_buttons(self):
        """Get all buttons

        Returns
        -------
        dict
            Dictionary of all buttons
        """
        return {"load": self.load_project_btn, "confirm": self.confirm_btn}

    def get_variables(self):
        """Get all variables

        Returns
        -------
        dict
            Dictionary of all variables
        """
        return {"project_name": self.project_name_var}

    def get_widgets(self):
        """Get all widgets

        Returns
        -------
        dict
            Dictionary of all widgets
        """
        return {
            "label_frame": self.label_frame,
            "show_segmentation": self.show_on_gui,
            "mark_position": self.mark_position,
        }
