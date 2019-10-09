#!/usr/bin/env python3
# coding: utf-8
from automanagemachine.components import utils
from automanagemachine.components.machine.machine_vbox import MachineVbox
from automanagemachine.components.requirements.requirements_vbox_sdk import RequirementsVboxSdk
from automanagemachine.core import cfg, logger

print(cfg['app']['name'] + " | version: " + cfg['app']['version'])

virtual_environment = cfg['machine']['virtual_environment']
if virtual_environment.lower() == "vbox":
    requirements = RequirementsVboxSdk()
    machine = MachineVbox()
elif virtual_environment.lower() == "aws":
    logger.warning("AWS not implemented.")
    utils.stop_program()
else:
    logger.critical("Not implemented.")
    utils.stop_program()

machine.name = cfg['machine']['name']
machine.cpu = cfg['machine']['cpu']
machine.virtual_memory = cfg['machine']['virtual_memory']
machine.create()
machine.run()
