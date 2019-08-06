#!/usr/bin/env python3
# coding: utf-8
from automanagemachine.components.machine.machine import Machine
from automanagemachine.components.machine.machine_aws import MachineAws
from automanagemachine.core import cfg
from automanagemachine.components.machine.machine_vbox import MachineVbox

print(cfg['app']['name'] + " | version: " + cfg['app']['version'])

determine_environment = cfg['machine']['api']

# TODO: Implement others environments
if determine_environment == "vbox":
    machine = MachineVbox()
elif determine_environment == "aws":
    machine = MachineAws()
else:
    machine = Machine()

machine.create()
