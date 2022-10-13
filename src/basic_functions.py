# -*- coding: utf-8 -*-
#
#  mfm2mqtt.py
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

# import standard modules
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import configparser
import logging
import os
#import signal
#import time
from datetime import datetime

__version__ = "0.0.2"
__version_date__ = "2022-10-13"
__description__ = "mfm2mqtt"
__license__ = "MIT"


default_log_level = logging.INFO

def parse_args():
    """parse command line arguments
    Also add current version and version date to description
    """
    parser = ArgumentParser(
        description=self_description + f"\nVersion: {__version__} ({__version_date__})",
        formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("-c", "--config", dest="config_file", default=default_config,
                        help="define config file (default: " + default_config + ")")
    parser.add_argument("-d", "--daemon", action='store_true',
                        help="define if the script is run as a systemd daemon")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="turn on verbose output to get debug logging")
    return parser.parse_args()


# noinspection PyUnusedLocal
def shutdown(exit_signal, frame):
    """
    Signal handler which ends the loop
    Parameters
    ----------
    exit_signal: int
        signal value
    frame: unused
    """
    global running
    logging.info(f"Program terminated. Signal {exit_signal}")
    running = False

def read_config(filename):
    """
    Read config ini file and return configparser object
    Parameters
    ----------
    filename: str
        path of ini file to parse
    Returns
    -------
    configparser.ConfigParser(): configparser object
    """
    config = None
    # check if config file exists
    if not os.path.isfile(filename):
        logging.error(f'Config file "{filename}" not found')
        exit(1)
    # check if config file is readable
    if not os.access(filename, os.R_OK):
        logging.error(f'Config file "{filename}" not readable')
        exit(1)
    try:
        config = configparser.ConfigParser()
        config.read(filename)
    except configparser.Error as e:
        logging.error("Config Error: %s", str(e))
        exit(1)
    logging.info("Done parsing config file")
    return config
