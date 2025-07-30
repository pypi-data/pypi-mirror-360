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
from tkinter import ttk
import logging

# Third Party Imports
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as tck

# Local Imports
from navigate.view.custom_widgets.popup import PopUp
from navigate.view.custom_widgets.LabelInputWidgetFactory import LabelInput
from navigate.view.custom_widgets.validation import ValidatedSpinbox

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class AutofocusPopup:
    """Class creates the popup to configure autofocus parameters."""

    def __init__(self, root, *args, **kwargs):
        """Initialize the AutofocusPopup class.

        Parameters
        ----------
        root : tk.Tk
            Root window.
        *args
            Variable length argument list.
        **kwargs
            Arbitrary keyword arguments.
        """
        # Creating popup window with this name and size/placement,
        # PopUp is a Toplevel window
        #: PopUp: PopUp window
        self.popup = PopUp(
            root, "Autofocus Settings", "+320+180", top=False, transient=False
        )
        # Change background of popup window to white
        self.popup.configure(bg="white")

        # Creating content frame
        content_frame = self.popup.get_frame()
        device_frame = tk.Frame(content_frame)
        device_frame.grid(row=0, columnspan=3, sticky=tk.NSEW)

        # Dictionary for all the variables
        #: dict: Dictionary of all the input widgets.
        self.inputs = {}
        #: dict: Dictionary of all the setting variables.
        self.setting_vars = {}

        self.inputs["device"] = LabelInput(
            parent=device_frame,
            label="Device:",
            input_class=ttk.Combobox,
            input_var=tk.StringVar(),
            input_args={"width": 20, "state": "readonly"},
            label_args={"padding": (0, 0, 10, 0)},
        )
        self.inputs["device"].grid(row=0, column=0, pady=3, padx=5)

        self.inputs["device_ref"] = LabelInput(
            parent=device_frame,
            label="Axis:",
            input_class=ttk.Combobox,
            input_var=tk.StringVar(),
            input_args={"width": 20, "state": "readonly"},
            label_args={"padding": (0, 0, 10, 0)},
        )
        self.inputs["device_ref"].grid(row=0, column=1, pady=3, padx=30)

        starting_row_id = 1

        # Row 0, Column Titles
        title_labels = [
            "Select",
            "Range  (" + "\N{GREEK SMALL LETTER MU}" + "m)",
            "Step Size  (" + "\N{GREEK SMALL LETTER MU}" + "m)"
        ]
        for i in range(3):
            title = ttk.Label(content_frame, text=title_labels[i], padding=(2, 5, 0, 0))
            title.grid(row=starting_row_id, column=i, sticky=tk.NSEW)

        # Row 1, 2 - Autofocus Settings
        setting_names = ["coarse", "fine", "robust_fit"]
        setting_labels = ["Coarse", "Fine", "Inverse Power Tent Fit"]
        for i in range(2):
            # Column 0 - Checkboxes
            variable = tk.BooleanVar(False)
            widget = ttk.Checkbutton(
                content_frame, text=setting_labels[i], variable=variable
            )
            widget.grid(row=i + 1 + starting_row_id, column=0, sticky=tk.NSEW, padx=5)
            self.setting_vars[setting_names[i] + "_selected"] = variable

            # Column 1 - Ranges
            widget = LabelInput(
                parent=content_frame,
                input_class=ValidatedSpinbox,
                input_var=tk.StringVar(),
                input_args={"from_": 0.0, "to": 50000},
            )
            widget.grid(
                row=i + 1 + starting_row_id,
                column=1,
                sticky=tk.NSEW,
                padx=(0, 5),
                pady=(15, 0),
            )
            self.inputs[setting_names[i] + "_range"] = widget
            self.setting_vars[setting_names[i] + "_range"] = widget.get_variable()

            # Column 2 - Step Sizes
            widget = LabelInput(
                parent=content_frame,
                input_class=ValidatedSpinbox,
                input_var=tk.StringVar(),
                input_args={"from_": 0.0, "to": 50000},
            )
            widget.grid(
                row=i + 1 + starting_row_id,
                column=2,
                sticky=tk.NSEW,
                padx=(0, 5),
                pady=(15, 0),
            )
            self.inputs[setting_names[i] + "_step_size"] = widget
            self.setting_vars[setting_names[i] + "_step_size"] = widget.get_variable()

        # Row 4, Autofocus Button
        #: ttk.Button: Autofocus button.
        self.autofocus_btn = ttk.Button(content_frame, text="Autofocus")
        self.autofocus_btn.grid(
            row=starting_row_id + 4, column=2, padx=(0, 25), pady=(10, 10), sticky=tk.E
        )

        variable = tk.BooleanVar(False)
        robust_fit = ttk.Checkbutton(
            content_frame, text=setting_labels[2], variable=variable
        )
        robust_fit.grid(row=starting_row_id + 4, column=0, sticky=tk.NSEW, padx=5)
        self.setting_vars["robust_fit"] = variable

        # Row 5, Plot
        #: matplotlib.figure.Figure: Figure for the plot.
        self.fig = Figure(figsize=(5, 5), dpi=100)
        #: matplotlib.axes.Axes: Axes for the plot.
        self.coarse = self.fig.add_subplot(111)
        self.coarse.set_title("Discrete Cosine Transform", fontsize=18)
        self.coarse.set_xlabel("Focus Stage Position", fontsize=16)
        self.coarse.yaxis.set_minor_locator(tck.AutoMinorLocator())
        self.coarse.xaxis.set_minor_locator(tck.AutoMinorLocator())

        self.fig.tight_layout()
        canvas = FigureCanvasTkAgg(self.fig, master=content_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(
            row=starting_row_id + 5,
            column=0,
            columnspan=3,
            sticky=tk.NSEW,
            padx=(5, 5),
            pady=(5, 5),
        )

    def get_widgets(self):
        """Returns the dictionary of input widgets.

        Returns
        -------
        dict
            Dictionary of all the input widgets.
        """
        return self.inputs
