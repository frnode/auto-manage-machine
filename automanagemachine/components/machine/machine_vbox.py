#!/usr/bin/env python3
# coding: utf-8
import datetime
import os
import virtualbox
from virtualbox.library import VBoxErrorIprtError, VBoxErrorObjectNotFound, OleErrorUnexpected, OleErrorInvalidarg, \
    VBoxErrorInvalidObjectState, VBoxErrorVmError, VBoxErrorMaximumReached, VBoxErrorFileError, VBoxErrorXmlError, \
    OleErrorAccessdenied

from automanagemachine.components import utils
from automanagemachine.components.machine.machine import Machine
from automanagemachine.core import cfg, logger


class MachineVbox(Machine):
    """
    Class inherited from Machine, it is used to initiate / conduct actions on a virtualbox machine
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
        Create a virtual machine under virtualbox using a .OVA file
        The name of the OVA appliance will be modified using the configuration file
        """
        __ova_file = os.getcwd() + "/data/ova/" + self.ova

        logger.info(
            "Machine settings: Name: '" + self.name + "' - Group: '" + self.machine_group + "' - OS: '" + self.os + "'")

        __appliance = self.vbox.create_appliance()
        __progress = __appliance.read(__ova_file)
        logger.info("Reading the .ova file...")

        try:
            __progress.wait_for_completion(-1)
        except VBoxErrorIprtError:
            logger.warning("Can not read .OVA file: " + __ova_file)
            utils.stop_program()

        __appliance.interpret()

        if __appliance.get_warnings() is not None:
            logger.warning(__appliance.get_warnings())
            utils.stop_program()

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
        logger.info("Creation/import in progress, wait...")

        try:
            __progress.wait_for_completion(-1)
        except VBoxErrorIprtError:
            logger.warning("Can not import the machine: " + __ova_file)
            utils.stop_program()

        logger.info("Machine created: " + self.name)

    def __modify(self):
        """
        Edit the created machine to set parameters
        """
        __vm = self.vbox.find_machine(self.name)

        try:
            __session = __vm.create_session()
        except VBoxErrorIprtError:
            logger.warning("Error creating guest session")
            utils.stop_program()
        except VBoxErrorMaximumReached:
            logger.warning("The maximum of concurrent guest sessions has been reached")
            utils.stop_program()

        __session.machine.cpu_execution_cap = int(self.cpu_execution_cap)
        __session.machine.memory_balloon_size = int(self.memory_balloon_size)
        __session.machine.description = "Created with " + cfg['app']['name'] + " on the " + datetime.datetime.now(). \
            strftime('%Y-%m-%d at %H:%M:%S.%f') + "\nBased on the appliance: " + self.ova_appliance_name

        try:
            __session.machine.save_settings()
        except VBoxErrorFileError:
            logger.warning("Settings file not accessible")
            utils.stop_program()
        except VBoxErrorXmlError:
            logger.warning("Could not parse the settings file")
            utils.stop_program()
        except OleErrorAccessdenied:
            logger.warning(" Modification request refused")
            utils.stop_program()

        __session.unlock_machine()

    def create(self):
        """
        Create a machine under virtualbox
        """
        Machine.create(self)
        self.__create_with_ova()
        self.__modify()

    def run(self):
        """
        Start a machine under virtualbox
        """
        logger.info("Starting the machine: " + self.name)
        __session = virtualbox.Session()
        __vm = self.__find_vm_by_uuid_or_name(self.name)

        try:
            __progress = __vm.launch_vm_process(__session, 'gui', '')
        except OleErrorUnexpected:
            logger.warning("Virtual machine not registered: " + self.name)
            utils.stop_program()
        except OleErrorInvalidarg:
            logger.warning("The session is invalid")
            utils.stop_program()
        except VBoxErrorObjectNotFound:
            logger.warning("The machine was not found: " + self.name)
            utils.stop_program()
        except VBoxErrorInvalidObjectState:
            logger.warning("The machine is already on or is being switched on")
            utils.stop_program()
        except VBoxErrorIprtError:
            logger.warning("Can not start the machine")
            utils.stop_program()
        except VBoxErrorVmError:
            logger.warning("Failed to assign machine to session")
            utils.stop_program()

        try:
            __progress.wait_for_completion(-1)
        except VBoxErrorIprtError:
            logger.warning("Can not start the machine")
            utils.stop_program()

        logger.info("Machine started")

    def __exist(self, name):
        """
        Check if a machine exists
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

    def __find_vm_by_uuid_or_name(self, uuid_or_uuid):
        """
        Look for a machine and return it
        :param uuid_or_uuid: Name of the machine or UUID
        :return: If the machine exists, return the machine
        """
        try:
            __vm = self.vbox.find_machine(uuid_or_uuid)
        except VBoxErrorObjectNotFound:
            logger.warning("Can not find the machine with the name/uuid: " + uuid_or_uuid)
            utils.stop_program()

        return __vm
