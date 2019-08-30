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
        self.vbox = virtualbox.VirtualBox()
        self.api = "vbox"

    def start(self, uuid):
        """
        TODO
        """
        logger.info('Start vbox machine: ' + uuid)
        __vm = self.__get_vm_by_uuid(uuid)
        __vbox = virtualbox.VirtualBox()
        __session = virtualbox.Session()
        __progress = __vm.launch_vm_process(__session, 'gui', '')
        __progress.wait_for_completion(5000)

        time.sleep(10)
        __session.console.keyboard.put_keys(
            press_keys=["DOWN", "DOWN", "ENTER", "DOWN", "DOWN", "DOWN", "DOWN", "DOWN", "DOWN", "ENTER"])
        time.sleep(60)
        __session.console.keyboard.put_keys(list(cfg['machine']['preseed']))
        logger.warning("Keyboard sended")
        __session.unlock_machine()
        return __vm

    def test(self):
        __ova_file = os.getcwd() + "/data/ova/" + cfg['machine']['ova']
        __test = self.vbox.create_appliance()
        __test.read(__ova_file)
        __test.interpret()
        __desc = __test.find_description("Debian_10_64")
        __desc.set_name("test")
        __desc.set_
        __test.import_machines()


    def run_install(self, machine):
        __iso_file = os.getcwd() + "/data/isos/" + cfg['machine']['iso']

        __installer = self.vbox.create_unattended_installer()
        __installer.iso_path = __iso_file
        __installer.machine = IMachine(machine)
        __installer.prepare()
        __installer.construct_media()
        __installer.reconfigure_vm()

    def create_with_ova(self):
        var = None

    def create(self):
        self.create_with_ova()

    def create_old(self, name, machine_group, machine_os):
        """
        Create a new machine
        :param name:
        :param machine_group:
        :param machine_os:
        """
        Machine.create(self)
        logger.info(
            "Machine settings: Name: '" + name + "' - Group: '" + machine_group + "' - OS: '" + machine_os + "'")

        __machine_exist = self.__exist(name)

        if __machine_exist is True:
            logger.warning("The name of the machine already exists: " + name)
            name = self.__generate_name(name)
            logger.info("Generating a new name: " + name)
        # __installer.detect_iso_os()

        try:
            __machine = self.vbox.create_machine("", name, [machine_group], machine_os, "")
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

        logger.info("Set machine parameters...")

        __machine.memory_size = int(cfg['machine']['ram'])
        __machine.memory_balloon_size = int(cfg['machine']['memory_balloon_size'])
        __machine.cpu_count = int(cfg['machine']['cpu'])
        __machine.cpu_execution_cap = int(cfg['machine']['cpu_execution_cap'])

        logger.info("Parameters set successfully, saving...")
        try:
            __machine.save_settings()
        except VBoxErrorFileError:
            logger.critical("Settings file not accessible")
            utils.stop_program()
        except VBoxErrorXmlError:
            logger.critical("Could not parse the settings file")
            utils.stop_program()
        except OleErrorAccessdenied:
            logger.critical("Modification request refused")
            utils.stop_program()

        try:
            self.vbox.register_machine(__machine)
        except (VBoxErrorObjectNotFound, VBoxErrorInvalidObjectState):
            logger.critical("Could not create machine")
            utils.stop_program()

        __location = virtualbox.library.ISystemProperties.default_machine_folder.fget(self.vbox.system_properties) + \
                     machine_group + "/" + name + "/"

        try:
            __medium = self.vbox.create_medium(format_p="", location=__location,
                                               access_mode=virtualbox.library.AccessMode(2),
                                               a_device_type_type=virtualbox.library.DeviceType(3))
        except VBoxErrorObjectNotFound:
            logger.critical("Invalid disk identifier")
            utils.stop_program()
        except VBoxErrorFileError:
            logger.critical("Invalid disk location")
            utils.stop_program()

        __hard_drive_bytes = int(cfg['machine']['hard_drive_gb']) * 1024 * 1024 * 1024

        try:
            __progress = __medium.create_base_storage(__hard_drive_bytes, [])
            __progress.wait_for_completion(50000)
        except VBoxErrorNotSupported:
            logger.critical("The variant of storage creation operation is not supported")
            utils.stop_program()
        except VBoxErrorIprtError:
            logger.critical("Failed to wait for task completion")
            utils.stop_program()

        __session = virtualbox.Session()

        try:
            __machine.lock_machine(__session, virtualbox.library.LockType(1))
        except OleErrorUnexpected:
            logger.critical("The machine is not registered")
            utils.stop_program()
        except OleErrorAccessdenied:
            logger.critical("Refused access, check rights")
            utils.stop_program()
        except VBoxErrorInvalidObjectState:
            logger.critical("Session already open or being opened")
            utils.stop_program()
        except VBoxErrorVmError:
            logger.critical("Failed to assign machine to session")
            utils.stop_program()

        __vm = __session.machine

        try:
            __controller = __vm.add_storage_controller("SATA", virtualbox.library.StorageBus(2))
        except VBoxErrorObjectInUse:
            logger.critical("A storage controller with given name exists already: " + __controller.name)
            utils.stop_program()
        except OleErrorInvalidarg:
            logger.critical("Invalid controller type")
            utils.stop_program()

        try:
            __vm.attach_device(__controller.name, 0, 0, __medium.device_type, __medium)
        except OleErrorInvalidarg:
            logger.critical("SATA device, SATA port, IDE port or IDE slot out of range, or file or UUID not found")
            utils.stop_program()
        except VBoxErrorInvalidObjectState:
            logger.critical("Machine must be registered before media can be attached")
            utils.stop_program()
        except VBoxErrorInvalidVmState:
            logger.critical("Invalid machine state")
            utils.stop_program()
        except VBoxErrorObjectInUse:
            logger.critical("A medium is already attached to this or another virtual machine")
            utils.stop_program()

        __iso_file = os.getcwd() + "/data/isos/" + cfg['machine']['iso']

        try:
            __dvd_medium = self.vbox.open_medium(__iso_file, virtualbox.library.DeviceType(2),
                                                 virtualbox.library.AccessMode(1),
                                                 True)
        except VBoxErrorFileError:
            logger.critical("Invalid medium storage file location or could not find the medium at the specified "
                            "location: " + __iso_file)
            utils.stop_program()
        except VBoxErrorIprtError:
            logger.critical("Could not get medium storage format")
            utils.stop_program()
        except OleErrorInvalidarg:
            logger.critical("Invalid medium storage format")
            utils.stop_program()
        except VBoxErrorInvalidObjectState:
            logger.critical("Medium has already been added to a media registry")
            utils.stop_program()

        try:
            __vm.attach_device(__controller.name, 1, 0, __medium.device_type, __dvd_medium)
        except OleErrorInvalidarg:
            logger.critical("SATA device, SATA port, IDE port or IDE slot out of range, or file or UUID not found")
            utils.stop_program()
        except VBoxErrorInvalidObjectState:
            logger.critical("Machine must be registered before media can be attached")
            utils.stop_program()
        except VBoxErrorInvalidVmState:
            logger.critical("Invalid machine state" + __machine.state)
            utils.stop_program()
        except VBoxErrorObjectInUse:
            logger.critical("A medium is already attached to this or another virtual machine")
            utils.stop_program()

        try:
            __vm.save_settings()
        except VBoxErrorFileError:
            logger.critical("Settings file not accessible")
            utils.stop_program()
        except VBoxErrorXmlError:
            logger.critical("Could not parse the settings file")
            utils.stop_program()
        except OleErrorAccessdenied:
            logger.critical("Modification request refused")
            utils.stop_program()

        try:
            __session.unlock_machine()
        except OleErrorUnexpected:
            logger.critical("Session is not locked")
            utils.stop_program()

        return __machine

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
