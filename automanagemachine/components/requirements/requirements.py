#!/usr/bin/env python3
# coding: utf-8
import os
import platform
import shutil
import urllib.request
import re
import zipfile
from automanagemachine.core import cfg, logger
import automanagemachine.components.utils as utils


class Requirements:
    """
    Checking the requirements before launching the program
    """

    def __init__(self):
        logger.info('Starting the common pre-requisite check...')
        self.python_version = None

    def verify(self):
        """
        Check and run the prerequisite tests
        """
        self.__minimal_python_version()

    def __minimal_python_version(self):
        """
        Check Python version
        """
        self.python_version = utils.python_version()
        __minimal_python_version = "3.0.0"

        logger.info("Check if Python is in minimum " + __minimal_python_version + " version")
        if utils.python_version() >= __minimal_python_version:
            logger.info("Good! Python " + utils.python_version() + " on " + platform.system())
        else:
            __text_error = "You must run the program under Python 3 minimum!"
            logger.critical(__text_error)
            utils.stop_program()
