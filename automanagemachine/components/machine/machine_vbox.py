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

import datetime
import os
import virtualbox
from virtualbox.library import VBoxErrorIprtError, VBoxErrorObjectNotFound, OleErrorUnexpected, OleErrorInvalidarg, \
    VBoxErrorInvalidObjectState, VBoxErrorVmError, VBoxErrorMaximumReached, VBoxErrorFileError, VBoxErrorXmlError, \
    OleErrorAccessdenied, NetworkAttachmentType, FileCopyFlag, IHostNetworkInterface
from virtualbox.library_base import VBoxError

from automanagemachine.components import utils
from automanagemachine.components.machine.machine import Machine
from automanagemachine.core import cfg, logger, cfg_vbox, MODULE_DIR

class MachineVbox(Machine):
    """
    Class inherited from Machine, it is used to initiate / conduct actions on a virtualbox machine
    """

    def __init__(self):
        Machine.__init__(self)
        logger.info("MachineVbox initialization...")
        self.vbox = virtualbox.VirtualBox()
        self.api = "vbox"
        self.ova = cfg_vbox['machine']['ova']
        self.ova_appliance_name = cfg_vbox['machine']['ova_appliance_name']
        self.machine_group = cfg['app']['name']
        self.cpu_execution_cap = int(cfg_vbox['machine']['cpu_execution_cap'])
        self.memory_balloon_size = int(cfg_vbox['machine']['memory_balloon_size'])
        self.script_copy_to_guest = cfg['machine']['script_copy_to_guest']
        self.script_copy_dest = cfg['machine']['script_copy_dest']

        self.network_attachement_type = int(cfg_vbox['machine']['network_attachement_type'])
        self.network_attachement_slot = int(cfg_vbox['machine']['network_attachement_slot'])

        self.network_bridged_interface = cfg_vbox['machine']['network_bridged_interface']
        self.network_internal_network = cfg_vbox['machine']['network_internal_network']
        self.network_host_only_interface = cfg_vbox['machine']['network_host_only_interface']
        self.network_generic_driver = cfg_vbox['machine']['network_generic_driver']
        self.network_nat_network_name = cfg_vbox['machine']['network_nat_network_name']

        self.network_host_only_interface_enable_type = int(
            cfg_vbox['machine']['network_host_only_interface_enable_type'])
        self.network_host_only_interface_static_ip_config_ip_address = \
            cfg_vbox['machine']['network_host_only_interface_static_ip_config_ip_address']
        self.network_host_only_interface_static_ip_config_network_mask = \
            cfg_vbox['machine']['network_host_only_interface_static_ip_config_network_mask']
        self.network_host_only_interface_static_ip_config_v6_ip_address = \
            cfg_vbox['machine']['network_host_only_interface_static_ip_config_v6_ip_address']
        self.network_host_only_interface_static_ip_config_v6_network_mask = \
            cfg_vbox['machine']['network_host_only_interface_static_ip_config_v6_network_mask']

        self.network_host_only_interface_dhcp_enable = bool(
            cfg_vbox['machine']['network_host_only_interface_dhcp_enable'])
        self.network_host_only_interface_dhcp_ip_address = \
            cfg_vbox['machine']['network_host_only_interface_dhcp_ip_address']
        self.network_host_only_interface_dhcp_network_mask = \
            cfg_vbox['machine']['network_host_only_interface_dhcp_network_mask']
        self.network_host_only_interface_dhcp_lower_ip_address = \
            cfg_vbox['machine']['network_host_only_interface_dhcp_lower_ip_address']
        self.network_host_only_interface_dhcp_upper_ip_address = \
            cfg_vbox['machine']['network_host_only_interface_dhcp_upper_ip_address']

        self.network_nat_network = cfg_vbox['machine']['network_nat_network']

    def __create_with_ova(self):
        """
        Create a virtual machine under virtualbox using a .OVA file
        The name of the OVA appliance will be modified using the configuration file
        """
        __ova_file = MODULE_DIR + "data/ova/" + self.ova

        logger.info(
            "Machine settings: Name: '" + self.name + "' - Group: '" + self.machine_group + "' - OS: '" + self.os + "'")

        __appliance = self.vbox.create_appliance()

        try:
            __appliance.read(__ova_file)
        except VBoxError:
            logger.warning("Can not read .OVA file: " + __ova_file)
            utils.stop_program()

        logger.info("Reading the .ova file (" + __ova_file + ") ...")

        __appliance.interpret()

        # if __appliance.get_warnings() is not None:
        #    logger.warning(__appliance.get_warnings())
        #    utils.stop_program()

        __desc = __appliance.find_description(self.ova_appliance_name)

        __machine_exist = self.__exist(self.name)

        if __machine_exist:
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

    def __configure(self):
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

        __adapter = __session.machine.get_network_adapter(self.network_attachement_slot)
        __adapter.enabled = True
        __adapter.cable_connected = True
        __adapter.attachment_type = NetworkAttachmentType(self.network_attachement_type)

        if self.network_attachement_type == 1:
            # NAT
            # Does not require more actions
            pass
        elif self.network_attachement_type == 2:
            # Bridged
            if self.network_bridged_interface == "default" or self.network_bridged_interface == "":
                # use the first network adapter of the operating system
                __selected_adapter_host = self.__verify_network_card(
                    name=self.__get_network_cards().__getitem__(0).name)
            else:
                # use the network adapter defined in the configuration
                __selected_adapter_host = self.__verify_network_card(name=self.network_bridged_interface)

            if __selected_adapter_host is None:
                logger.warning("The network card for bridge access does not exist")
                utils.stop_program()

            __adapter.bridged_interface = __selected_adapter_host.name

        elif self.network_attachement_type == 3:
            # Internal
            __adapter.internal_network = self.network_internal_network
        elif self.network_attachement_type == 4:
            # Host Only
            # TODO: Not fully implemented. DHCP options can not save...
            if self.network_host_only_interface == "":
                # create a new network interface
                __host = virtualbox.library.IHost(self.vbox.host)

                try:
                    # BUG: Values are reversed, use host_interface first
                    __host_interface, __progress = __host.create_host_only_network_interface()
                except OleErrorInvalidarg:
                    logger.warning("The network card already exists: " + __host_interface.id_p)
                    utils.stop_program()

                logger.info(__progress.operation_description)
                __progress.wait_for_completion(-1)

                __selected_adapter_host = self.__verify_network_card(name=__host_interface.id_p)
                logger.info("New network card created: " + __host_interface.id_p)
                __adapter.host_only_interface = __selected_adapter_host.name

                if self.network_host_only_interface_enable_type == 1:
                    __selected_adapter_host.enable_static_ip_config(
                        self.network_host_only_interface_static_ip_config_ip_address,
                        self.network_host_only_interface_static_ip_config_network_mask)
                elif self.network_host_only_interface_enable_type == 2:
                    __selected_adapter_host.enable_static_ip_config_v6(
                        self.network_host_only_interface_static_ip_config_v6_ip_address,
                        self.network_host_only_interface_static_ip_config_v6_network_mask)
                elif self.network_host_only_interface_enable_type == 3:
                    __selected_adapter_host.enable_dynamic_ip_config()

                if self.network_host_only_interface_dhcp_enable:
                    try:
                        __dhcp = self.vbox.find_dhcp_server_by_network_name(__selected_adapter_host.name)
                    except:
                        __dhcp = self.vbox.create_dhcp_server(__selected_adapter_host.name)

                    if __dhcp:
                        __dhcp.set_configuration(ip_address=self.network_host_only_interface_dhcp_ip_address,
                                                 network_mask=self.network_host_only_interface_dhcp_network_mask,
                                                 from_ip_address=self.network_host_only_interface_dhcp_lower_ip_address,
                                                 to_ip_address=self.network_host_only_interface_dhcp_upper_ip_address)
                        __dhcp.enabled = True
                        __dhcp.start(__selected_adapter_host.network_name, __selected_adapter_host.name, "netadp")
            else:
                # Use an existing host only configuration and use the network adapter defined in the configuration
                __selected_adapter_host = self.__verify_network_card(name=self.network_host_only_interface)
                __adapter.host_only_interface = __selected_adapter_host.name

        elif self.network_attachement_type == 5:
            # Generic
            __adapter.generic_driver = self.network_generic_driver
        elif self.network_attachement_type == 6:
            # NAT Network
            # TODO: Not fully implemented. Missing network ports redirection and some options
            __nat_network = self.__verify_nat_network(self.network_nat_network_name)

            if not __nat_network:
                __nat_network = self.vbox.create_nat_network(self.network_nat_network_name)

            __adapter.nat_network = __nat_network.network_name
            __nat_network.enabled = True
            __nat_network.network = self.network_nat_network

        try:
            __session.machine.save_settings()
        except VBoxErrorFileError:
            logger.warning("Settings file not accessible")
            utils.stop_program()
        except VBoxErrorXmlError:
            logger.warning("Could not parse the settings file")
            utils.stop_program()
        except OleErrorAccessdenied:
            logger.warning("Modification request refused")
            utils.stop_program()

        __session.unlock_machine()

    def create(self):
        """
        Create a machine under virtualbox
        """
        Machine.create(self)
        self.__create_with_ova()
        self.__configure()

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
            logger.critical("Virtual machine not registered: " + self.name)
            utils.stop_program()
        except OleErrorInvalidarg:
            logger.critical("The session is invalid")
            utils.stop_program()
        except VBoxErrorObjectNotFound:
            logger.critical("The machine was not found: " + self.name)
            utils.stop_program()
        except VBoxErrorInvalidObjectState:
            logger.critical("The machine is already on or is being switched on")
            utils.stop_program()
        except VBoxErrorIprtError:
            logger.critical("Can not start the machine")
            utils.stop_program()
        except VBoxErrorVmError:
            logger.critical("Failed to assign machine to session")
            utils.stop_program()

        try:
            __progress.wait_for_completion(-1)
        except VBoxErrorIprtError:
            logger.warning("Can not start the machine")
            utils.stop_program()

        logger.info("Machine started")

        if self.command:
            self.__run_command(__session)

        __session.unlock_machine()

        logger.info("Machine started")

    def __run_command(self, __session):
        """
        Execute a command on the defined session
        :param __session: Session where to send the execution command
        """
        Machine.run_command(self)
        try:
            __guest_session = __session.console.guest.create_session(self.username, self.password)
        except VBoxErrorIprtError:
            logger.critical("Error creating guest session")
            utils.stop_program()
        except VBoxErrorMaximumReached:
            logger.critical("The maximum of concurrent guest sessions has been reached")
            utils.stop_program()
        except SystemError:
            logger.critical("Can not create the session on the machine")
            utils.stop_program()

        if self.script_copy_to_guest:
            __tmp_file_to_guest = MODULE_DIR + "data/scripts/" + self.script_copy_to_guest
            __tmp_file_copy = __guest_session.file_copy_to_guest(__tmp_file_to_guest, self.script_copy_dest,
                                                                 [FileCopyFlag(0)])

        proc, stdout, stderr = __guest_session.execute(self.command, self.command_args)

        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')
        logger.info("Result of the script/command:")
        if stdout:
            logger.info(stdout)

        if stderr:
            logger.error(stderr)

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

        if __machine_exist:
            return self.__generate_name(original_name)

        return __generated_name

    def __find_vm_by_uuid_or_name(self, uuid_or_name):
        """
        Look for a machine and return it
        :param uuid_or_name: Name of the machine or UUID
        :return: If the machine exists, return the machine
        """
        try:
            __vm = self.vbox.find_machine(uuid_or_name)
        except VBoxErrorObjectNotFound:
            logger.critical("Can not find the machine with the name/uuid: " + uuid_or_name)
            utils.stop_program()

        return __vm

    def __verify_network_card(self, name):
        """
        Check that the network card is valid
        :param name: Name of the network card
        :return: Network adapter object or None
        """
        __host_network_cards = self.__get_network_cards()

        for adapter in __host_network_cards:
            if adapter.name == name:
                return adapter

        logger.warning("The network card for host only does not exist")
        utils.stop_program()
        return None

    def __verify_nat_network(self, network_name):
        """
        Check nat network is valid
        :param network_name: Name of the network
        :return: Nat object or None
        """
        __nat_networks = self.vbox.nat_networks

        for nat in __nat_networks:
            if nat.network_name == network_name:
                return nat

        return None

    def __get_network_cards(self):
        """
        Returns the network cards of the hosts
        :return: List of network cards of the hosts
        """
        __host = virtualbox.library.IHost(self.vbox.host)
        __adapters_host = __host.network_interfaces

        if not isinstance(__adapters_host, list):
            raise TypeError("network_cards can only be an instance of type list")
        for a in __adapters_host[:10]:
            if not isinstance(a, IHostNetworkInterface):
                raise TypeError("array can only contain objects of type IHostNetworkInterface")

        return __adapters_host
