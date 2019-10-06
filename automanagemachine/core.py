#!/usr/bin/env python3
# coding: utf-8
import configparser
import logging

import coloredlogs

cfg = configparser.ConfigParser()  # initialize configparser with the cfg variable
cfg.read('config/config.ini')

cfg_vbox = configparser.ConfigParser()  # initialize configparser with the cfg_vbox variable
cfg_vbox.read('config/config_vbox.ini')

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
logging.basicConfig(filename=cfg['app']['name'] + ".log", filemode='w', format=format_logger,
                    datefmt=format_logger_time)
coloredlogs.install(level='DEBUG', logger=logger, fmt=format_logger)

# 'application' code
# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')
