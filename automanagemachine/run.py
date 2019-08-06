#!/usr/bin/env python3
# coding: utf-8
from automanagemachine.core import cfg
from automanagemachine.components.machine.machine import Machine
from automanagemachine.components.machine.machine_aws import MachineAws
from automanagemachine.components.machine.machine_vbox import MachineVbox
from automanagemachine.components.prerequisites import Prerequisites

print(cfg['app']['name'] + " | version: " + cfg['app']['version'])

prerequisites = Prerequisites()
prerequisites.check()
print(prerequisites.vbox_sdk_get_latest_stable_version())

determine_environment = cfg['machine']['api']

# TODO: Implement others environments
if determine_environment == "vbox":
    machine = MachineVbox()
elif determine_environment == "aws":
    machine = MachineAws()
else:
    machine = Machine()

machine.create()


