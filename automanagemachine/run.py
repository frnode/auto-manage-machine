#!/usr/bin/env python3
# coding: utf-8
from automanagemachine.core import cfg
from automanagemachine.components.machine.machine import Machine
from automanagemachine.components.machine.machine_aws import MachineAws
from automanagemachine.components.machine.machine_vbox import MachineVbox
from automanagemachine.components.prerequisites import Prerequisites
from automanagemachine.utils import run_python_script

print(cfg['app']['name'] + " | version: " + cfg['app']['version'])

prerequisites = Prerequisites()
# prerequisites.check_python()
# prerequisites.vbox_sdk()

determine_environment = cfg['machine']['api']

#run_python_script("test")

# # TODO: Implement others environments
# if determine_environment == "vbox":
#     machine = MachineVbox()
# elif determine_environment == "aws":
#     machine = MachineAws()
# else:
#     machine = Machine()
#
# machine.create()


