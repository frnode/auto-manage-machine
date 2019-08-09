#!/usr/bin/env python3
# coding: utf-8
import virtualbox

from automanagemachine.components.machine.machine import Machine
from automanagemachine.core import cfg


class MachineVbox(Machine):
    """
    TODO
    """
    def __init__(self):
        self.api = "vbox"
        self.vbox = virtualbox.VirtualBox()
        Machine.__init__(self)

    def start(self):
        """
        TODO
        """
        print('Start vbox machine')

    def create(self, name, machine_group, os):
        """
        Create a new machine
        """
        Machine.create(self)
        __machine = self.vbox.create_machine("", name, [machine_group], os, "")
        return self.vbox.register_machine(__machine)
