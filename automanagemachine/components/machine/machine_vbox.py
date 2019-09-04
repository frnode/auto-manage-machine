#!/usr/bin/env python3
# coding: utf-8
import datetime
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
        self.cpu_execution_cap = int(cfg['machine']['cpu_execution_cap'])
        self.memory_balloon_size = int(cfg['machine']['memory_balloon_size'])

    def __create_with_ova(self):
        """
        Create VM with .OVA file
        """
        __ova_file = os.getcwd() + "/data/ova/" + self.ova

        logger.info(
            "Machine settings: Name: '" + self.name + "' - Group: '" + self.machine_group + "' - OS: '" + self.os + "'")

        __appliance = self.vbox.create_appliance()
        __progress = __appliance.read(__ova_file)
        logger.info("Reading the .ova file...")
        __progress.wait_for_completion(-1)
        __appliance.interpret()

        if __appliance.get_warnings() is not None:
            logger.warning(__appliance.get_warnings())

        __desc = __appliance.find_description(self.ova_appliance_name)

        __machine_exist = self.__exist(self.name)

        if __machine_exist is True:
            logger.warning("The name of the machine already exists: " + self.name)
            self.name = self.__generate_name(self.name)
            logger.info("Generating a new name: " + self.name)

        logger.info("Applying settings...")
        __desc.set_name(self.name)
        __desc.set_cpu(self.cpu)
        __desc.set_memory(self.virtual_memory)

        __progress = __appliance.import_machines()
        logger.info("Creation in progress, wait...")
        __progress.wait_for_completion(-1)
        logger.info("Machine created: " + self.name)

    def __modify(self):
        """
        Edit the created machine
        """
        __vm = self.vbox.find_machine(self.name)
        __session = __vm.create_session()

        __session.machine.cpu_execution_cap = int(self.cpu_execution_cap)
        __session.machine.memory_balloon_size = int(self.memory_balloon_size)
        __session.machine.description = "Created with " + cfg['app']['name'] + " on the " + datetime.datetime.now().\
            strftime('%Y-%m-%d at %H:%M:%S.%f') + "\nBased on the appliance: " + self.ova_appliance_name

        __session.machine.save_settings()
        __session.unlock_machine()

    def create(self):
        """
        Create machine
        """
        Machine.create(self)
        self.__create_with_ova()
        self.__modify()

    def run(self):
        """
        Launch machine machine
        """
        logger.info("Starting the machine: " + self.name)
        __session = virtualbox.Session()
        __vm = self.vbox.find_machine(self.name)
        __progress = __vm.launch_vm_process(__session, 'gui', '')
        __progress.wait_for_completion()
        logger.info("Machine started")

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
