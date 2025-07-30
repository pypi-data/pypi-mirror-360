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
from time import time
import logging
from functools import wraps

# Third Party Imports

# Local Imports


def function_timer(func):
    """Decorator for evaluating the duration of time necessary to execute a statement.

    Parameters
    ----------
    func : function
        The function to be timed.

    Returns
    -------
    wrap_func : function
        The wrapped function.
    """

    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f"Function {func.__name__!r} executed in {(t2 - t1):.4f}s")
        return result

    return wrap_func


class FeatureList(object):
    def __init__(self, func):
        self._feature_list = func
        temp = func.__name__
        self.feature_list_name = str.title(temp.replace("_", " "))

    def __call__(self, *args, **kwargs):
        return self._feature_list()


class AcquisitionMode(object):
    def __init__(self, obj):
        self.__obj_class = obj
        self.__is_acquisition_mode = True

    def __call__(self, *args):
        return self.__obj_class(*args)


def log_initialization(cls):
    """Decorator for logging the initialization of a device class.

    Parameters
    ----------
    cls : class
        The class to be logged.

    Returns
    -------
    cls : class
        The class with the logging decorator.
    """

    # Get the original __init__ method
    original_init = cls.__init__

    @wraps(original_init)
    def new_init(self, *args, **kwargs):
        module_location = cls.__module__
        logger = logging.getLogger(module_location.split(".")[1])
        try:
            original_init(self, *args, **kwargs)
            logger.info(f"{cls.__name__}, " f"{args}, " f"{kwargs}")
        except Exception as e:
            logger.error(f"{cls.__name__} Initialization Failed")
            logger.error(f"Input args & kwargs: {args}, {kwargs}")
            logger.error(f"Error: {e}")
            raise e

    # Replace the original __init__ method with the new one
    cls.__init__ = new_init
    return cls
