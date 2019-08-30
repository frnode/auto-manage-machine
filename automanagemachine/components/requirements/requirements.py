#!/usr/bin/env python3
# coding: utf-8
import platform

from automanagemachine.components.machine.machine_vbox import MachineVbox
from automanagemachine.core import cfg, logger
import automanagemachine.components.utils as utils


class Requirements:
    """
    Checking the requirements before launching the program
    """

    def __init__(self):
        logger.info('Starting the common pre-requisite check...')
        self.python_version = utils.python_version()
        self.python_minimal_version = "3.0.0"
        self.virtual_environment = cfg['machine']['virtual_environment']

    def verify(self):
        """
        Check and run the prerequisite tests
        """
        self.__minimal_python_version()

    def run(self):
        """
        Run process requirements
        """
        self.verify()

    def __minimal_python_version(self):
        """
        Check Python version
        """
        logger.info("Check if Python is in minimum " + self.python_minimal_version + " version")
        if self.python_version >= self.python_minimal_version:
            logger.info("Good! Python " + self.python_version + " on " + platform.system())
        else:
            __text_error = "You must run the program under Python 3 minimum!"
            logger.critical(__text_error)
            utils.stop_program()
