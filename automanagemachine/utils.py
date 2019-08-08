#!/usr/bin/env python3
# coding: utf-8
import os
import platform
import sys

from automanagemachine.core import logger


def python_version():
    """
    Return python version
    """
    return platform.python_version()


def run_python_script(command, path_to_run=os.getcwd()):
    """
    Launch a python script
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

    os.system(command)  # Run the command
    # TODO: Need add try ?

    try:
        os.chdir(__current_dir)  # Reset execution directory
    except FileNotFoundError:
        __text_error = "The specified folder can not be found: " + path_to_run
        logger.critical(__text_error)
        stop_program()


def stop_program(text):
    """
    Quit program with specified text
    :param text: Text display for error
    """
    sys.exit()
