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

import configparser
import logging
from os.path import dirname, abspath, join

import coloredlogs

BASE_DIR = dirname(dirname(abspath(__file__)))
MODULE_DIR = join(BASE_DIR, 'automanagemachine/')

cfg = configparser.ConfigParser()  # initialize configparser with the cfg variable
cfg.read(MODULE_DIR + 'config/config.ini')

cfg_vbox = configparser.ConfigParser()  # initialize configparser with the cfg_vbox variable
cfg_vbox.read(MODULE_DIR + 'config/config_vbox.ini')

# create logger
logger = logging.getLogger(cfg['app']['name'])
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
format_logger = '%(asctime)s - %(hostname)s - %(name)s - %(levelname)s - %(message)s'
format_logger_time = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(format_logger, format_logger_time)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logging.basicConfig(filename=BASE_DIR + "/" + cfg['app']['name'] + ".log", filemode='w', format=format_logger,
                    datefmt=format_logger_time)
coloredlogs.install(level='DEBUG', logger=logger, fmt=format_logger)

# 'application' code
# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')
