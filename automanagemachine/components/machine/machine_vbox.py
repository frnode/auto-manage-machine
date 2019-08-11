#!/usr/bin/env python3
# coding: utf-8
import re

import virtualbox
from virtualbox.library import VBoxErrorObjectNotFound, VBoxErrorInvalidObjectState, VBoxErrorFileError, \
    OleErrorInvalidarg

from automanagemachine.components import utils
from automanagemachine.components.machine.machine import Machine
from automanagemachine.core import cfg, logger


class MachineVbox(Machine):
    """
    TODO
    """

    def __init__(self):
        Machine.__init__(self)
        self.vbox = virtualbox.VirtualBox()
        self.api = "vbox"

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
        logger.info("Machine settings: Name: '" + name + "' - Group: '" + machine_group + "' - OS: '" + os + "'")

        __machine_exist = self.__exist(name)

        if __machine_exist is True:
            logger.warning("The name of the machine already exists: " + name)
            name = self.__generate_name(name)
            logger.info("Generating a new name: " + name)

        try:
            __machine = self.vbox.create_machine("", name, [machine_group], os, "")
        except VBoxErrorObjectNotFound:
            logger.critical("The operating system of the machine is invalid")
            utils.stop_program()
        except VBoxErrorFileError:
            logger.critical("Resulting settings file name is invalid or the settings file already exists or could not "
                            "be created due to an I/O error.")
            utils.stop_program()
        except OleErrorInvalidarg:
            logger.critical("Invalid machine name, or null group")
            utils.stop_program()

        try:
            self.vbox.register_machine(__machine)
        except (VBoxErrorObjectNotFound, VBoxErrorInvalidObjectState):
            logger.critical("Could not create machine")
            utils.stop_program()




    def __exist(self, name):
        """
        :param name: Name of machine
        :return: Bool
        """
        for __vm_name in self.vbox.machines:
            if str(__vm_name) == name:
                return True
        return False

    def __generate_name(self, original_name):
        """
        Generate a name from a base name
        :param name: Base name
        :return: Base name with a random string
        """
        __generated_name = original_name + "_" + utils.generate_random_str(10)
        __machine_exist = self.__exist(__generated_name)

        if __machine_exist is True:
            return self.__generate_name(original_name)

        return __generated_name
