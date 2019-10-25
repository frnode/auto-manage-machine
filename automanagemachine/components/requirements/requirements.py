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

import platform

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
