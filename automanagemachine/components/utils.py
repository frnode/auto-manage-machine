#!/usr/bin/env python3
# coding: utf-8
import os
import platform
import subprocess
import sys
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


def stop_program():
    """
    Quit program
    """
    sys.exit()
