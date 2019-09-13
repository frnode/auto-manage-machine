#!/usr/bin/env python3
# coding: utf-8
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
        logger.info('Wait ' + str(self.command_wait_time) + ' seconds before starting the command ...')
        time.sleep(self.command_wait_time)
        logger.info('Run command...')
