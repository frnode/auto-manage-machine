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
