#!/usr/bin/env python3
# coding: utf-8
from automanagemachine.components.machine.machine import Machine


class MachineVbox(Machine):
    """
    TODO
    """
    def __init__(self):
        Machine.__init__(self)
        self.api = "vbox"

    def start(self):
        """
        TODO
        """
        print('Start vbox machine')

    def create(self):
        """
        TODO
        :return:
        """
        Machine.create(self)


