#!/usr/bin/env python3
# coding: utf-8
from automanagemachine.components.requirements.requirements_vbox_sdk import RequirementsVboxSdk
from automanagemachine.core import cfg

print(cfg['app']['name'] + " | version: " + cfg['app']['version'])

determine_environment = cfg['machine']['api']

# TODO: Implement others environments
if determine_environment == "vbox":
    requirements = RequirementsVboxSdk()
    # machine = MachineVbox()
elif determine_environment == "aws":
    # machine = MachineAws()
    print("todo")
else:
    print("todo")
    # machine = Machine()

requirements.verify()
