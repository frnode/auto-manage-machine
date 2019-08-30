#!/usr/bin/env python3
# coding: utf-8
from automanagemachine.components import utils
from automanagemachine.components.machine.machine_vbox import MachineVbox
from automanagemachine.components.requirements.requirements import Requirements
from automanagemachine.components.requirements.requirements_vbox_sdk import RequirementsVboxSdk
from automanagemachine.core import cfg, logger

print(cfg['app']['name'] + " | version: " + cfg['app']['version'])

virtual_environment = cfg['machine']['virtual_environment']
if virtual_environment == "vbox":
    requirements = RequirementsVboxSdk()
    machine = MachineVbox()
elif virtual_environment == "aws":
    logger.warning("AWS not implemented.")
    utils.stop_program()
else:
    logger.critical("Not implemented.")
    utils.stop_program()

machine.name = cfg['machine']['name']
machine.cpu = cfg['machine']['cpu']
machine.virtual_memory = cfg['machine']['virtual_memory']
machine.create()

# TODO: Implement others environments
# if determine_environment == "vbox":
#     requirements = RequirementsVboxSdk()
#     machine = MachineVbox()
# elif determine_environment == "aws":
#     logger.warning("AWS not implemented.")
#     utils.stop_program()
# else:
#     logger.critical("Not implemented.")
#     utils.stop_program()

#requirements.verify()
## vm = machine.create(cfg['machine']['name'], "/" + cfg['app']['name'], cfg['machine']['environment'])
#machine.test()
## machine.test()
## vm = machine.create_using_ova(cfg['machine']['name'])
##machine.start(cfg['machine']['name'])
#