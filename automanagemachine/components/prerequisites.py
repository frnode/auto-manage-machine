#!/usr/bin/env python3
# coding: utf-8
import os
import platform
import sys
import urllib.request
import re

from automanagemachine.core import cfg


class Prerequisites:
    """
    Checking the prerequisites before launching the program
    """

    def __init__(self):
        print("Start check prerequisites...")

    def check_python(self):
        """
        Check prerequisites
        """
        if self.__python_version() == 1:
            print("Python " + str(self.__python_version_int[0]) + "." + str(self.__python_version_int[1]) +
                  "." + str(self.__python_version_int[2]) + " on " + platform.system())
        else:
            print("You must run the program under Python 3 minimum!")
            # TODO: Exception, stop program

    def __python_version(self):
        """
        Check if the python environment is at least version 3
        :return: Return 1 if it's OK else 0
        """
        self.__python_version_int = sys.version_info

        if self.__python_version_int >= (3, 0):
            return 1  # return 1 if it's ok
        else:
            return 0

    def vbox_sdk(self):
        """
        Download the VBOX SDK
        :return:
        """
        if cfg['sdk']['vbox_sdk'] == "latest":
            print('check or download latest version vbox sdk')
            print("VBOX SDK: " + self.vbox_sdk_get_latest_stable_version())
        else:
            __regex_test = re.search("^\d+(\.\d+){2,2}$", cfg['sdk']['vbox_sdk'])
            if __regex_test is None:
                print('Please check the value of "vbox_sdk" in the configuration file, it must contain 3 numbers '
                      'separated by points.')
            # TODO: Exception, stop program
            elif __regex_test is not None:
                print("VBOX SDK: " + __regex_test.group())

    def vbox_sdk_get_latest_stable_version(self):
        """
        Get latest stable version of vbox sdk
        :return:
        """
        __latest_stable_version = urllib.request.Request(cfg['sdk']['vbox_url_latest_stable_version'])
        with urllib.request.urlopen(__latest_stable_version) as response:
            __latest_stable_version = response.read().decode().rstrip()

        __regex_test = re.search("^\d+(\.\d+){2,2}$", __latest_stable_version)

        if __regex_test is None:
            print('The value of the version does not match the regex, it must contain 3 numbers separated by points. '
                  'Check with the following URL: ' + cfg['sdk']['vbox_url_latest_stable_version'])
            # TODO: Exception, stop program

        return __latest_stable_version

    def vbox_sdk_download(self):
        """
        TODO
        :return:
        """

    def vbox_sdk_install(self):
        """
        TODO
        :return:
        """
