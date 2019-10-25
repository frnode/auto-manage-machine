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

import configparser
import time

from automanagemachine.core import logger, cfg


class Machine:
    """
    Class to create a basic machine object, initialized by the inheritance class
    """

    def __init__(self):
        logger.info("Machine initialization...")
        self.api = None
        self.cpu = 1
        self.virtual_memory = 1024
        self.name = "default-name"
        self.os = cfg['machine']['os']
        self.command = cfg['machine']['command']
        self.command_args = cfg['machine']['command_args'].split("\n")
        self.command_wait_time = int(cfg['machine']['command_wait_time'])
        self.username = cfg['machine']['username']
        self.password = cfg['machine']['password']

    def start(self):
        """
        Start a machine, basic behavior
        """
        print('Machine is starting...')

    def create(self):
        """
        Create a new machine, basic behavior
        """
        logger.info("Create new " + str.upper(self.api) + " machine...")

    def run_command(self):
        """
        Run command, basic behavior
        """
        logger.info('Wait ' + str(self.command_wait_time) + ' seconds before starting the command...')
        time.sleep(self.command_wait_time)
        logger.info('Run command...wait!')
