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

# Standard library imports
import tkinter as tk
from tkinter import ttk
from decimal import Decimal, InvalidOperation
import logging

# Third party imports

# Local imports
from navigate.view.custom_widgets.hover import Hover

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)

REGEX_DICT = {
    "float": "(^-?$)|(^-?[0-9]+\\.?[0-9]*$)",
    "float_nonnegative": "(^$)|(^[0-9]+\\.?[0-9]*$)",
    "int": "^-?[0-9]*$",
    "int_nonnegative": "^[0-9]*$",
}

"""
Base design courtesy:
Learning Path: Python GUI Programming - A Complete Reference Guide by Alan D. Moore
and B. M. Harwani

The below classes take advantage of multiple inheritance to achieve validation.

Validation Events: none, focusin, focusout, focus, key, all
- Focus is whether user is using widget
- Key is when user is typing keystrokes

Substitution Codes for validation in tkinter: %P, %s, %i, %S, %v, %V, %W, %d
- %P = proposed value from user
- %s = value currently in field
- %i = index of text being edited. String
- %S = text being inserted or deleted
- %v = widgets validate value
- %V = event that triggered validation
- %W = widgets name in TK as string
- %d = code that indicates action attempted. 0 for delete, 1 for insert, -1 for other.

String Tkinter Validation process:
- validate sets the event that triggers callback
- validatecommand takes in command that determines if data is valid
- invalidcommand runs command given if validatecommand is False

A python callable is passed to a .register function for the widget
def someFun(): do something
def otherFun(): do something
widget = ttk.Entry()
wrapped_function = widget.register(someFun)
other_function = widget.register(otherFun)
validation_function = (wrapped_function, '%P') # Can use any amount of substitution
codes above to pass in various data
invalid = (other_function, '%P', '%s')
widget.config(
            validate='all',
            validatecommand=validation_function with args,
            invalidcommand=invalid_function with args
)

"""


class ValidatedMixin:
    """Validation functions

    These functions are used to validate the input of the widget. They are called
    by the validatecommand attribute of the widget. They return True if the input
    is valid and False if it is not. They also set the error string to be displayed
    in the widget.
    """

    # error_var
    def __init__(self, *args, error_var=None, **kwargs):
        """Initialize the ValidatedMixin

        Parameters
        ----------
        *args
            Variable length argument list
        error_var : tk.StringVar
            The variable to store the error message in
            if error_var = None, creates its own variable
        **kwargs
            Keyword arguments to pass to the parent class
        """
        #: tk.StringVar: The variable to store the error message in
        self.error = error_var or tk.StringVar()

        # Calls class that is mixed in with this class
        super().__init__(*args, **kwargs)

        # History for each widgets to undo and redo
        #: list: The undo history of the widget
        self.undo_history = []

        #: list: The redo history of the widget
        self.redo_history = []

        # Validation setup
        validcmd = self.register(self._validate)
        invalidcmd = self.register(self._invalid)

        # Tkinter widget validation setup
        # Includes all validation events keystroke and focus
        self.config(
            validate="all",
            validatecommand=(
                validcmd,
                "%P",
                "%s",
                "%S",
                "%V",
                "%i",
                "%d",
            ),
            # pass in all sub codes/data
            invalidcommand=(invalidcmd, "%P", "%s", "%S", "%V", "%i", "%d"),
        )
        #: Hover: The hover bubble for the widget
        self.hover = Hover(self, text=None, type="free")
        self.hover_flag = kwargs.get("hover_flag", False)

    def _toggle_error(self, on=False):
        """Toggle the error message

        Error handler - Customize color or what happens to widget
        Changes text to red on error

        Parameters
        ----------
        on : bool
            Whether to turn the error message on or off

        """
        self.config(foreground=("red" if on else "black"))

    def _validate(self, proposed, current, char, event, index, action):
        """Validate the input of the widget

        Parameters
        ----------
        proposed : str
            The proposed value of the widget
        current : str
            The current value of the widget
        char : str
            The character being inserted or deleted
        event : str
            The event that triggered the validation
        index : str
            The index of the character being inserted or deleted
        action : str
            The action being performed. 0 for delete, 1 for insert, -1 for other

        Returns
        -------
        bool
            True if the input is valid, False if it is not
        """
        self._toggle_error(False)  # Error is off
        self.error.set("")  # No error to start
        valid = True  # Again true means no error
        if event == "focusout":  # Leaving widget
            valid = self._focusout_validate(event=event)
            if valid:
                self.add_history(event)
            else:
                if self.undo_history:
                    self.set(self.undo_history[-1])
                    self.undo_history.pop()
                    self._toggle_error(False)
                    valid = True
        elif event == "key":  # Keystroke into widget
            valid = self._key_validate(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action,
            )
            if valid:
                self.add_history(event)
        return valid

    def _focusout_validate(self, **kwargs):
        """Validate the input of the widget when focus is lost.

        Parameters
        ----------
        **kwargs
            Keyword arguments to pass to the validation function

        Returns
        -------
        bool
            True if the input is valid, False if it is not

        """
        return True

    def _key_validate(self, **kwargs):
        """Validate the input of the widget when a key is pressed.

        Parameters
        ----------
        **kwargs
            Keyword arguments to pass to the validation function

        Returns
        -------
        bool
            True if the input is valid, False if it is not

        """
        return True

    # Invalid
    def _invalid(self, proposed, current, char, event, index, action):
        """Handle the invalid input of the widget

        Parameters
        ----------
        proposed : str
            The proposed value of the widget
        current : str
            The current value of the widget
        char : str
            The character being inserted or deleted
        event : str
            The event that triggered the validation
        index : str
            The index of the character being inserted or deleted
        action : str
            The action being performed. 0 for delete, 1 for insert, -1 for other

        """
        if event == "focusout":
            self._focusout_invalid(event=event)
        elif event == "key":
            self._key_invalid(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action,
            )

    def _focusout_invalid(self, **kwargs):
        """Handle the invalid input of the widget when focus is lost.

        Parameters
        ----------
        **kwargs
            Keyword arguments to pass to the invalid function

        """
        self._toggle_error(True)

    def _key_invalid(self, **kwargs):
        """Handle the invalid input of the widget when a key is pressed.

        Parameters
        ----------
        **kwargs
            Keyword arguments to pass to the invalid function

        """
        pass

    # Allows a manual check on entered values to be used whenever needed
    def trigger_focusout_validation(self):
        """Trigger the focusout validation of the widget"""
        valid = self._validate("", "", "", "focusout", "", "")
        if not valid:
            self._focusout_invalid(event="focusout")
        return valid

    def add_history(self, event):
        """Add the current value to the history of the widget.

        Parameters
        ----------
        event : tk.Event
            The event that triggered the history addition
        """
        value = self.get()
        if value != "":
            # Don't add duplicates
            if self.undo_history and self.undo_history[-1] == value:
                pass
            else:
                self.undo_history.append(value)
                self.redo_history = []
            if len(self.undo_history) > 3:
                self.undo_history.pop(0)

    def undo(self, event):
        """Undo the last change to the widget.

        Parameters
        ----------
        event : tk.Event
            The event that triggered the undo
        """
        if self.undo_history:
            # Get the redo value
            value = self.undo_history.pop()
            if self.redo_history and self.redo_history[-1] == self.get():
                pass
            else:
                self.redo_history.append(self.get())
            if len(self.redo_history) > 3:
                self.redo_history.pop(0)

            self.set(value)
            return True
        return False

    def redo(self, event):
        """Redo the last change that was undone.

        Parameters
        ----------
        event : tk.Event
            The event that triggered the redo

        """
        if self.redo_history:
            value = self.get()
            # add back to undo_history
            self.undo_history.append(value)
            if len(self.undo_history) > 3:
                self.undo_history.pop(0)
            value = self.redo_history.pop()
            self.set(value)
            return True
        return False


class ValidatedEntry(ValidatedMixin, ttk.Entry):
    """A validated entry widget

    Entry class that requires Entry
    Can optionally pass in a precision, min value, max value and a boolean for
    whether the entry requires a value. The min_var, max_var, and focus_update_var
    are the same as a spinbox
    """

    def __init__(
        self,
        *args,
        precision=0,
        required=False,
        min_var=None,
        max_var=None,
        focus_update_var=None,
        min="-Infinity",
        max="Infinity",
        **kwargs,
    ):
        """Initialise the entry widget

        Parameters
        ----------
        parent : tk.Widget
            The parent widget
        precision : int, optional
            The precision of the entry, by default 0
        min_var : tk.Variable, optional
            The minimum value of the entry, by default None
        max_var : tk.Variable, optional
            The maximum value of the entry, by default None
        required : bool, optional
            Whether the entry requires a value, by default False
        focus_update_var : tk.Variable, optional
            The variable to update when focus is lost, by default None
        min : str, optional
            The minimum value of the entry, by default "-Infinity"
        max : str, optional
            The maximum value of the entry, by default "Infinity"
        **kwargs
            Keyword arguments to pass to the entry
        """
        super().__init__(*args, **kwargs)
        #: Decimal: The resolution of the entry
        self.resolution = Decimal(precision)  # Number for precision given on creation
        #: int: The precision of the entry
        self.precision = (
            self.resolution.normalize().as_tuple().exponent
        )  # Precision of number as exponent
        #: tk.StringVar: The variable to store the value of the entry in
        self.variable = kwargs.get("textvariable") or tk.StringVar()
        #: str: The minimum value of the entry
        self.min = float(min)
        #: str: The maximum value of the entry
        self.max = float(max)
        #: bool: Whether the entry requires a value
        self.required = required
        self.is_fake_focusout = False

    def set(self, value):
        """Set the value of the entry to the given value.

        Parameters
        ----------
        value : str
            The value to set the entry to

        Examples
        --------
        >>> widget = ValidatedEntry(parent)
        >>> widget.set('1')
        """
        # self.delete(0, tk.END)
        self.variable.set(value)
        # self.insert(0, value)

    def set_precision(self, prec):
        """Set the precision of the entry in decimal places.

        Given a precision it will update the spinboxes ability to handle more or less
        precision for validation. This is separate from the increment value.

        Parameters
        ----------
        prec : int
            The precision to set the entry to

        Examples
        --------
        >>> widget = ValidatedEntry(parent)
        >>> widget.set_precision(1)
        """
        self.precision = prec

    def _get_precision(self):
        """Get the precision of the entry

        Returns
        -------
        int
            The precision of the entry

        Examples
        --------
        >>> widget = ValidatedEntry(parent)
        >>> widget._get_precision()
        """
        nums_after = self.resolution.find(".")

        return (-1) * len(self.resolution[nums_after + 1 :])

    def _key_validate(self, char, index, current, proposed, action, **kwargs):
        """Validate the input of the entry when a key is pressed.

        Parameters
        ----------
        char : str
            The character being inserted or deleted
        index : int
            The index of the character being inserted or deleted
        current : str
            The current value of the entry
        proposed : str
            The proposed value of the entry
        action : str
            The action being performed
        **kwargs
            Keyword arguments to pass to the invalid function

        Returns
        -------
        bool
            Whether the input is valid

        Examples
        --------
        >>> widget = ValidatedEntry(parent)
        """
        self.is_fake_focusout = True

        # Allow deletion
        if action == "0":
            if proposed == "":
                self.is_fake_focusout = False
                return True
            self._is_valid_proposed_value(proposed)
            return True

        return self._is_valid_proposed_value(proposed)

    def _is_valid_proposed_value(self, proposed):
        """Validate a proposed value

        Returns
        -------
        bool
            True if the proposed is valid, False if not
        """
        min_val = float(self.min)
        max_val = float(self.max)

        if proposed == "-":
            self._toggle_error(True)
            self.is_fake_focusout = False
            return min_val < 0

        if proposed == ".":
            self._toggle_error(True)
            self.is_fake_focusout = False
            return True

        # Proposed value is a Decimal, so convert and check further
        try:
            proposed = Decimal(proposed)
        except InvalidOperation:
            self.is_fake_focusout = False
            return False
        proposed_precision = proposed.as_tuple().exponent
        if any([(proposed > max_val), (proposed_precision < self.precision)]):
            return False

        if proposed < min_val:
            self._toggle_error(True)
            return True

        self._toggle_error(False)

        return True

    def _focusout_validate(self, event):
        """Validate the input of the entry when focus is lost.

        If entry widget is empty set the error string and return False

        Parameters
        ----------
        event : tk.Event
            The event that triggered the validation

        Returns
        -------
        bool
            Whether the input is valid

        Examples
        --------
        >>> widget = ValidatedEntry(parent)
        """
        valid = True
        value = self.get()
        max_val = self.max
        min_val = self.min

        # Check for error upon leaving widget
        if value.strip() == "" and self.required:
            self.error.set("A value is required")
            return False
        else:
            self.error.set("")

        try:
            value = Decimal(value)
        except InvalidOperation:
            self.error.set("Invalid number string: {}".format(value))
            return False

        # check if there are range limits
        if min_val == "-Infinity" or max_val == "Infinity":
            return True

        # Checking if greater than minimum
        if value < float(min_val):
            self.error.set("Value is too low (min {})".format(min_val))
            valid = False

        # Checking if less than max
        if value > float(max_val):
            self.error.set("Value is too high (max {})".format(max_val))

        # If input is valid on focusout add to history of widget
        return valid

    def _set_focus_update_var(self, event):
        """Set the focus update variable to the current value of the entry

        Parameters
        ----------
        event : tk.Event
            The event that triggered the update

        Examples
        --------
        >>> widget = ValidatedEntry(parent)
        """
        value = self.get()
        if self.focus_update_var and not self.error.get():
            self.focus_update_var.set(value)

    def _set_minimum(self, *args):
        """Set the minimum value of the entry when focus is lost.

        Parameters
        ----------
        *args
            Arguments to pass to the invalid function
        """
        current = self.get()
        try:
            new_min = self.min_var.get()
            self.min = float(new_min)
        except (tk.TclError, ValueError):
            pass
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()  # Revalidate with the new minimum

    def _set_maximum(self, *args):
        """Set the maximum value of the entry when focus is lost.

        Parameters
        ----------
        *args
            Arguments to pass to the invalid function.
        """
        current = self.get()
        try:
            new_max = self.max_var.get()
            self.max = float(new_max)
        except (tk.TclError, ValueError):
            pass
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()  # Revalidate with the new maximum

    def _toggle_error(self, on=False):
        """Toggle the error state of the entry.

        Parameters
        ----------
        on : bool
            Whether to turn the error state on or off


        """
        super()._toggle_error(on)
        if on and self.hover_flag:
            self.hover.seterror(self.error.get())
        else:
            self.hover.hidetip()

    def _validate(self, proposed, current, char, event, index, action):
        """Validate the input of the widget

        Parameters
        ----------
        proposed : str
            The proposed value of the widget
        current : str
            The current value of the widget
        char : str
            The character being inserted or deleted
        event : str
            The event that triggered the validation
        index : str
            The index of the character being inserted or deleted
        action : str
            The action being performed. 0 for delete, 1 for insert, -1 for other

        Returns
        -------
        bool
            True if the input is valid, False if it is not
        """
        self._toggle_error(False)  # Error is off
        self.error.set("")  # No error to start
        valid = True  # Again true means no error
        if event == "focusout":  # Leaving widget
            valid = self._focusout_validate(event=event)
            if self.is_fake_focusout:
                self.is_fake_focusout = False
                return valid
            if valid:
                self.add_history(event)
            else:
                if self.undo_history:
                    self.is_fake_focusout = True
                    self.set(self.undo_history[-1])
                    self.undo_history.pop()
                    self._toggle_error(False)
                    valid = True
        elif event == "key":  # Keystroke into widget
            valid = self._key_validate(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action,
            )
            if valid:
                self.add_history(event)
        return valid

    def add_history(self, event):
        """Add the current value to the history of the widget.

        Parameters
        ----------
        event : tk.Event
            The event that triggered the history addition
        """
        value = self.get()
        if value != "":
            min_val = float(self.min)
            max_val = float(self.max)
            # Don't add duplicates
            if self.undo_history and self.undo_history[-1] == value:
                pass
            elif (
                value != "-"
                and value != "."
                and Decimal(value) >= min_val
                and Decimal(value) <= max_val
            ):
                self.undo_history.append(value)
            if len(self.undo_history) > 3:
                self.undo_history.pop(0)

    def undo(self, event):
        """Undo the last change to the widget.

        Parameters
        ----------
        event : tk.Event
            The event that triggered the undo
        """
        if self.undo_history:
            # Get the redo value
            value = self.undo_history.pop()
            if self.redo_history and self.redo_history[-1] == self.get():
                pass
            else:
                self.redo_history.append(self.get())
            if len(self.redo_history) > 3:
                self.redo_history.pop(0)
            # self.set() will trigger one focusout event
            self.is_fake_focusout = True
            self.set(value)
            return True
        return False

    def redo(self, event):
        """Redo the last change that was undone.

        Parameters
        ----------
        event : tk.Event
            The event that triggered the redo

        """
        if self.redo_history:
            value = self.get()
            # add back to undo_history
            self.undo_history.append(value)
            if len(self.undo_history) > 3:
                self.undo_history.pop(0)
            value = self.redo_history.pop()
            # self.set() will trigger one focusout event
            self.is_fake_focusout = True
            self.set(value)
            return True
        return False


class ValidatedCombobox(ValidatedMixin, ttk.Combobox):
    """A validated combobox.

    Parameters
    ----------
    master : tk.Widget
        The parent widget
    values : list
        The values to display in the combobox
    required : bool
        Whether the combobox requires a value
    **kwargs
        Keyword arguments to pass to the combobox
    """

    def _key_validate(self, proposed, action, **kwargs):
        """Validate the input of the combobox when a key is pressed.

        Parameters
        ----------
        proposed : str
            The proposed value of the combobox
        action : str
            The action being performed
        **kwargs
            Keyword arguments to pass to the invalid function

        Returns
        -------
        bool
            Whether the input is valid
        """
        valid = True

        # Clear field with delete or backspace
        if action == "0":
            self.set("")
            return True

        # Get list of combo values
        values = self.cget("values")

        # Check for words typed in if they match then set to that value
        matching = [x for x in values if x.lower().startswith(proposed.lower())]
        if len(matching) == 0:
            valid = False
        elif len(matching) == 1:
            self.set(matching[0])
            self.icursor(tk.END)
            valid = False
        return valid

    def _focusout_validate(self, **kwargs):
        """Validate the input of the combobox when focus is lost and set the error.

        Parameters
        ----------
        **kwargs
            Keyword arguments to pass to the invalid function

        Returns
        -------
        bool
            Whether the input is valid
        """
        valid = True
        if not self.get():
            valid = False
            self.error.set("A value is required")
        return valid


class ValidatedSpinbox(ValidatedMixin, ttk.Spinbox):
    """A spinbox that validates input and can be linked to other widgets.

    Deletion always allowed, digits always allowed, if from < 0 '-' is allowed as first
    char, if increment is decimal '.' allowed, if proposed value is greater than to
    ignore key if proposed value requires more precision than increment, ignore key
    On focus out, make sure number is a valid number string and greater than from value
    If given a min_var, max_var, or focus_update_var, then the spinbox range will
    update dynamically when those valuse are changed (can be used to link to other
    widgets)
    """

    def __init__(
        self,
        *args,
        min_var=None,
        max_var=None,
        focus_update_var=None,
        required=False,
        **kwargs,
    ):
        """Initialize the spinbox

        Parameters
        ----------
        master : tk.Widget
            The parent widget
        from_ : int or float
            The minimum value of the spinbox
        to : int or float
            The maximum value of the spinbox
        increment : int or float
            The increment of the spinbox
        min_var : tk.Variable
            A variable that will be used to update the minimum value of the spinbox
        max_var : tk.Variable
            A variable that will be used to update the maximum value of the spinbox
        focus_update_var : tk.Variable
            A variable that will be used to update the value of the spinbox when it
            loses focus
        no_negative : bool
            If True, the spinbox will not allow negative values
        no_decimal : bool
            If True, the spinbox will not allow decimal values
        required : bool
            If True, the spinbox will require a value
        precision : int
            The number of decimal places allowed in the spinbox

        """
        super().__init__(*args, **kwargs)

        #: Decimal: The resolution of the spinbox
        self.resolution = str(kwargs.get("increment", "1.0"))  # Number put into spinbox

        #: int: The precision of the spinbox
        self.precision = self._get_precision()

        #: tk.StringVar: The variable to store the value of the spinbox in
        self.variable = kwargs.get("textvariable") or tk.DoubleVar()

        #: bool: Whether the spinbox requires a value
        self.required = required

        # Dynamic range checker
        if min_var:
            #: str: The minimum value of the spinbox
            self.min_var = min_var
            self.min_var.trace_add("write", self._set_minimum)

        if max_var:
            #: str: The maximum value of the spinbox
            self.max_var = max_var
            self.max_var.trace_add("write", self._set_maximum)

        #: tk.StringVar: The variable to update when the spinbox loses focus
        self.focus_update_var = focus_update_var

        self.bind("<FocusOut>", self._set_focus_update_var)

    def set_precision(self, prec):
        """Set the precision of the spinbox in decimal places.

        Given a precision it will update the spinboxes ability to handle more or less
        precision for validation. This is separate from the increment value.

        Parameters
        ----------
        prec : int
            The number of decimal places allowed in the spinbox

        Examples
        --------
        >>> spinbox.set_precision(2)
        """
        self.precision = prec

    def _get_precision(self):
        """Get the precision of the spinbox in decimal places.

        Returns
        -------
        int
            The number of decimal places allowed in the spinbox

        Examples
        --------
        >>> spinbox._get_precision()
        """

        nums_after = self.resolution.find(".")
        return (-1) * len(self.resolution[nums_after + 1 :])

    def _key_validate(self, char, index, current, proposed, action, **kwargs):
        """Validate the key pressed in the spinbox.

        Parameters
        ----------
        char : str
            The character of the key pressed
        index : int
            The index of the cursor
        current : str
            The current value of the spinbox
        proposed : str
            The proposed value of the spinbox
        action : str
            The action of the key pressed
        **kwargs
            Additional keyword arguments

        Returns
        -------
        bool
            True if the key is valid, False if not

        Examples
        --------
        >>> spinbox._key_validate('1', 0, '0', '1', 'insert')
        """
        # Allow deletion
        if action == "0":
            if proposed == "":
                return True
            self._is_valid_proposed_value(proposed)
            return True

        return self._is_valid_proposed_value(proposed)

    def _is_valid_proposed_value(self, proposed):
        """Validate a proposed value

        Returns
        -------
        bool
            True if the proposed is valid, False if not
        """
        min_val = self.cget("from")
        max_val = self.cget("to")

        if proposed == "-" or proposed == ".":
            self._toggle_error(True)
            return True

        # Proposed value is a Decimal, so convert and check further
        try:
            proposed = Decimal(proposed)
        except InvalidOperation:
            return False
        proposed_precision = proposed.as_tuple().exponent

        if any([(proposed > max_val), (proposed_precision < self.precision)]):
            return False

        if proposed < min_val:
            self._toggle_error(True)
            return True

        self._toggle_error(False)

        return True

    def _focusout_validate(self, event):
        """Validate the spinbox when it loses focus and set the error message.

        Parameters
        ----------
        event : tk.Event
            The event that triggered the validation

        Returns
        -------
        bool
            True if the spinbox is valid, False if not
        """
        valid = True
        value = self.get()

        max_val = self.cget("to")
        min_val = self.cget("from")
        try:
            max_val = Decimal(str(max_val))
            min_val = Decimal(str(min_val))
        except InvalidOperation:
            err_str = f"Either {min_val} or {max_val} couldn't be cast to a Decimal."
            logger.debug(err_str)
            print(err_str)

        # Check for error upon leaving widget
        if value.strip() == "" and self.required:
            self.error.set("A value is required")
            return False
        else:
            self.error.set("")

        try:
            value = Decimal(str(value))
        except InvalidOperation:
            self.error.set("Invalid Number Provided: {}".format(value))
            return False

        # Checking if greater than minimum
        if value < min_val:
            self.error.set(f"Minimum Value: {min_val:.3f}")
            valid = False

        # Checking if less than max
        if value > max_val:
            self.error.set(f"Maximum Value: {max_val:.3f}")
            valid = False

        return valid

    # Gets current value of widget and if focus_update_var is present it sets it to the
    # same value
    def _set_focus_update_var(self, event):
        """Set the focus update variable to the current value of the spinbox.

        Parameters
        ----------
        event : tk.Event
            The event that triggered the function

        Examples
        --------
        >>> spinbox._set_focus_update_var(event)
        """
        value = self.get()
        if self.focus_update_var and not self.error.get():
            self.focus_update_var.set(value)

    def _set_minimum(self, *args):
        """Set the minimum value of the spinbox when focus is lost.

        Parameters
        ----------
        *args
            Additional arguments

        Examples
        --------
        >>> spinbox._set_minimum()
        """
        current = self.get()
        try:
            new_min = self.min_var.get()
            self.config(from_=new_min)
        except (tk.TclError, ValueError):
            pass
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()  # Revalidate with the new minimum

    def _set_maximum(self, *args):
        """Set the maximum value of the spinbox when focus is lost.

        Parameters
        ----------
        *args
            Additional arguments

        Examples
        --------
        >>> spinbox._set_maximum()
        """
        current = self.get()
        try:
            new_max = self.max_var.get()
            self.config(to=new_max)
        except (tk.TclError, ValueError):
            pass
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()  # Revalidate with the new maximum

    def _toggle_error(self, on=False):
        """Toggle the error message of the spinbox.

        Parameters
        ----------
        on : bool, optional
            Whether to turn the error on or off, by default False

        Examples
        --------
        >>> spinbox._toggle_error()
        """
        super()._toggle_error(on)
        if on and self.hover_flag:
            self.hover.seterror(self.error.get())
        else:
            self.hover.hidetip()

    def add_history(self, event):
        """Add the current value to the history of the widget.

        Parameters
        ----------
        event : tk.Event
            The event that triggered the history addition
        """
        value = self.get()
        if value != "":
            min_val = self.cget("from")
            max_val = self.cget("to")
            # Don't add duplicates
            if self.undo_history and self.undo_history[-1] == value:
                pass
            elif (
                value != "-"
                and value != "."
                and Decimal(value) >= min_val
                and Decimal(value) <= max_val
            ):
                self.undo_history.append(value)
                self.redo_history = []
            if len(self.undo_history) > 3:
                self.undo_history.pop(0)
