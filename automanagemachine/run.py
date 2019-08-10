#!/usr/bin/env python3
# coding: utf-8
from automanagemachine.components import utils
from automanagemachine.components.machine.machine_vbox import MachineVbox
from automanagemachine.components.requirements.requirements_vbox_sdk import RequirementsVboxSdk
from automanagemachine.core import cfg, logger

print(cfg['app']['name'] + " | version: " + cfg['app']['version'])

determine_environment = cfg['machine']['api']

# TODO: Implement others environments
if determine_environment == "vbox":
    requirements = RequirementsVboxSdk()
    machine = MachineVbox()
elif determine_environment == "aws":
    logger.warning("AWS not implemented.")
    utils.stop_program()
else:
    logger.critical("Not implemented.")
    utils.stop_program()

requirements.verify()
machine.create(cfg['machine']['name'], "/" + cfg['app']['name'], cfg['machine']['environment'])
