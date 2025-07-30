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
import argparse
from pathlib import Path

# Third Party Imports

# Local Imports
from navigate.config import get_configuration_paths


def evaluate_parser_input_arguments(args):
    """If non-default configuration, experiment, or ETL constant file is provided as an
    input argument.

    Accepts a ArgumentParser object
    Retrieves the default configuration/experiment/etc paths.
    Adds  non-default parser arguments to the ArgumentParser object
    Parses the object, and returns the desired configuration/experiment/etc paths.

    Parameters
    ----------
    args : argparse.Namespace
        Dictionary of parser input arguments

    Returns
    -------
    configuration_path : str
        Path to configuration file.
    experiment_path : str
        Path to experiment file
    waveform_constants_path : str
        Path to remote focusing and galvo waveform constants file
    rest_api_path : str
        Path to REST API file
    waveform_templates_path : str
        Path to waveform templates file
    logging_path : str
        Path to non-default logging location
    configurator : bool
        True if configurator is enabled
    gui_configuration_path
        Path to gui_configuration file
    multi_positions_path
        Path to multi_positions file
    """
    # Retrieve the Default Configuration paths
    (
        configuration_path,
        experiment_path,
        waveform_constants_path,
        rest_api_path,
        waveform_templates_path,
        gui_configuration_path,
        multi_positions_path,
    ) = get_configuration_paths()

    # Evaluate Input Arguments
    if args.configurator:
        configurator = True
    else:
        configurator = False

    if args.config_file:
        assert args.config_file.exists(), "Configuration file Path {} not valid".format(
            args.config_file
        )
        configuration_path = args.config_file

    if args.experiment_file:
        assert (
            args.experiment_file.exists()
        ), "experiment_file file Path {} not valid".format(args.experiment_file)
        experiment_path = args.experiment_file

    if args.waveform_constants_file:
        assert (
            args.waveform_constants_path.exists()
        ), "waveform_constants_path Path {} not valid".format(
            args.waveform_constants_path
        )
        waveform_constants_path = args.waveform_constants_path

    if args.rest_api_file:
        assert args.rest_api_file.exists(), "rest_api_file Path {} not valid".format(
            args.rest_api_file
        )
        rest_api_path = args.rest_api_file

    if args.waveform_templates_file:
        assert (
            args.waveform_templates_file.exists()
        ), "waveform_templates Path {} not valid".format(args.waveform_templates_file)
        waveform_templates_path = args.waveform_templates_file

    if args.gui_config_file:
        assert (
            args.gui_config_file.exists()
        ), "gui_configuration Path {} not valid".format(args.gui_config_file)
        gui_configuration_path = args.gui_config_file

    if args.multi_positions_file:
        assert (
            args.multi_positions_file.exists()
        ), "multi_positions Path {} not valid".format(args.multi_positions_file)
        multi_positions_path = args.multi_positions_file

    # Creating Loggers etc., they exist globally so no need to pass
    if args.logging_config:
        assert args.logging_config.exists(), "Logging Config Path {} not valid".format(
            args.logging_config
        )
        logging_path = args.logging_config
    else:
        logging_path = None

    return (
        configuration_path,
        experiment_path,
        waveform_constants_path,
        rest_api_path,
        waveform_templates_path,
        logging_path,
        configurator,
        gui_configuration_path,
        multi_positions_path,
    )


def create_parser():
    """Add Parser Input Arguments to ArgumentParser Object.

    Returns
    -------
    parser : object
        ArgumentParserObject with Added Input Arguments"""

    parser = argparse.ArgumentParser(description="navigate Command Line Arguments")

    input_args = parser.add_argument_group("Input Arguments")

    input_args.add_argument(
        "-c",
        "--configurator",
        required=False,
        default=False,
        action="store_true",
        help="Configurator - " "GUI for preparing a configuration.yaml file..",
    )

    input_args.add_argument(
        "-sh",
        "--synthetic-hardware",
        required=False,
        default=False,
        action="store_true",
        help="Synthetic Hardware - "
        "Allows launching of the software without the physical devices attached.",
    )

    input_args.add_argument(
        "-d",
        required=False,
        default=False,
        action="store_true",
        help="Enables debugging tool menu to be accessible.",
    )

    # Non-Default Configuration and Experiment Input Arguments
    input_args.add_argument(
        "--config-file",
        type=Path,
        required=False,
        default=None,
        help="Non-default path to the configuration.yml file.  \n"
        "This file sets the default global physical"
        "state of the microscope.  For example, number of lasers, number of cameras, "
        "digital I/O, analog I/O, etc.",
    )

    input_args.add_argument(
        "--gui-config-file",
        type=Path,
        required=False,
        default=None,
        help="Non-default path to the gui_config.yml file.  \n"
        "This file sets the default graphical user interface parameters, such as the "
        "default number of channels, spinbox values, etc.",
    )

    input_args.add_argument(
        "--experiment-file",
        type=Path,
        required=False,
        default=None,
        help="Non-default path to the experiment.yml file. \n"
        "This file sets the default user-specified "
        "physical state of the microscope. For example, how many channels, "
        "and what are their exposure time, filter position, laser, etc. ",
    )

    input_args.add_argument(
        "--waveform-constants-file",
        type=Path,
        required=False,
        default=None,
        help="Non-default path to the waveform_constants.yml file.  \n"
        "This file specifies the wavelength- and zoom-specific amplitude and offset "
        "of the ETL waveform generation.",
    )

    input_args.add_argument(
        "--rest-api-file",
        type=Path,
        required=False,
        default=None,
        help="Non-default path to the rest_api_config.yml config file \n"
        "This file specifies urls of restful api services.",
    )

    input_args.add_argument(
        "--waveform-templates-file",
        type=Path,
        required=False,
        default=None,
        help="Non-default path to the waveform_templates.yml config file \n"
        "This file specifies all waveform templates.",
    )

    input_args.add_argument(
        "--logging-config",
        type=Path,
        required=False,
        default=None,
        help="Non-default path to the logging.yml config file \n"
        "This file specifies how the logging will be performed.",
    )

    input_args.add_argument(
        "--multi-positions-file",
        type=Path,
        required=False,
        default=None,
        help="Non-default path to the multi_positions.yml file.  \n"
        "This file contains a list of stage positions.",
    )

    return parser
