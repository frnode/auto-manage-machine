#!/usr/bin/env python3
# coding: utf-8
import os
import time

import virtualbox
from virtualbox.library import OleErrorInvalidarg, VBoxErrorFileError, VBoxErrorInvalidObjectState, \
    VBoxErrorObjectNotFound, VBoxErrorNotSupported, VBoxErrorIprtError, VBoxErrorXmlError, OleErrorAccessdenied, \
    OleErrorUnexpected, VBoxErrorVmError, VBoxErrorObjectInUse, VBoxErrorInvalidVmState, IUnattended
from virtualbox.library_ext import IMachine

from automanagemachine.components import utils
from automanagemachine.components.machine.machine import Machine
from automanagemachine.core import cfg, logger


class MachineVbox(Machine):
    """
    TODO
    """

    def __init__(self):
        Machine.__init__(self)
        logger.info("MachineVbox initialization...")
        self.vbox = virtualbox.VirtualBox()
        self.api = "vbox"
        self.ova = cfg['machine']['ova']
        self.ova_appliance_name = cfg['machine']['ova_appliance_name']
        self.machine_group = cfg['app']['name']

    def create_with_ova(self):
        """
        Create VM with .OVA file
        """
        __ova_file = os.getcwd() + "/data/ova/" + self.ova
        __appliance = self.vbox.create_appliance()
        __appliance.read(__ova_file)
        __appliance.interpret()
        __desc = __appliance.find_description(self.ova_appliance_name)

        logger.info(
            "Machine settings: Name: '" + self.name + "' - Group: '" + self.machine_group + "' - OS: '" + self.os + "'")

        __machine_exist = self.__exist(self.name)

        if __machine_exist is True:
            logger.warning("The name of the machine already exists: " + self.name)
            self.name = self.__generate_name(self.name)
            logger.info("Generating a new name: " + self.name)

        __desc.set_name(self.name)
        __desc.set_cpu(self.cpu)
        __desc.set_memory(self.virtual_memory)
        __appliance.import_machines()


    def create(self):
        Machine.create(self)
        self.create_with_ova()

    def __exist(self, name):
        """
        :return: Bool
        :param name: Name of machine
        """
        for __vm_name in self.vbox.machines:
            if str(__vm_name) == name:
                return True
        return False

    def __generate_name(self, original_name):
        """
        Generate a name from a base name
        :param original_name: Base name
        :return: Base name with a random string
        """
        __generated_name = original_name + "_" + utils.generate_random_str(10)
        __machine_exist = self.__exist(__generated_name)

        if __machine_exist is True:
            return self.__generate_name(original_name)

        return __generated_name

    def __get_vm_by_uuid(self, uuid):
        __vbox = virtualbox.VirtualBox()
        __vm = __vbox.find_machine(uuid)
        return __vm
