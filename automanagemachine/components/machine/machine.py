#!/usr/bin/env python3
# coding: utf-8
from automanagemachine.core import logger


class Machine:
    """
    TODO
    """

    def __init__(self):
        logger.info("Machine initialization...")
        self.api = None
        self.cpu = 1
        self.memory = 1024


    def say_hello(self):
        """
        Just say hello...
        """
        print('Hello ? Are you here ?')

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
