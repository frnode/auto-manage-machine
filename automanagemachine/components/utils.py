#!/usr/bin/env python3
# coding: utf-8

#  auto-manage-machine
#  Copyright (C) 2019 - Node
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import platform
import subprocess
import sys
import uuid
import zipfile

from automanagemachine.core import logger


def python_version():
    """
    Return python version
    """
    return platform.python_version()


def run_python_script(command, path_to_run=os.getcwd(), output=False):
    """
    Launch a python script
    :param output: Output of the command executed
    :param path_to_run: Directory where the script is to be started. Default: current directory
    :param command: Command to launch the script
    """
    try:
        __current_dir = os.getcwd()  # Save the current execution directory
    except FileNotFoundError:
        __text_error = "The current execution directory does not exist"
        logger.critical(__text_error)
        stop_program()

    try:
        os.chdir(path_to_run)  # Change the execution directory
    except FileNotFoundError:
        __text_error = "The specified folder can not be found: " + path_to_run
        logger.critical(__text_error)
        stop_program()

    if output is False:
        subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    else:
        subprocess.call(command, shell=True)

    try:
        os.chdir(__current_dir)  # Reset execution directory
    except FileNotFoundError:
        __text_error = "The specified folder can not be found: " + path_to_run
        logger.critical(__text_error)
        stop_program()


def unzip_file(file, to):
    """
    Unzip file
    :param file: Zip file (to extract)
    :param to: Location of extraction
    """
    if zipfile.is_zipfile(file) is False:
        __text_error = "Invalid ZIP file: " + file
        logger.critical(__text_error)
        stop_program()

    try:
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(to)
    except zipfile.BadZipFile:
        __text_error = "Invalid ZIP file: " + file
        logger.critical(__text_error)
        stop_program()
    except zipfile.LargeZipFile:
        __text_error = "ZIP file size exceeds 4GB: " + file
        logger.critical(__text_error)
        stop_program()


def generate_random_str(length=6):
    """
    Generate a string of random characters
    :param length: Length of the string
    :return: String of characters
    """
    return uuid.uuid4().hex[:length].upper()


def stop_program():
    """
    Quit program
    """
    sys.exit()

