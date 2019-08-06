#!/usr/bin/env python3
# coding: utf-8
import os
import platform
import sys
import urllib.request

from automanagemachine.core import cfg

class Prerequisites:
    """
    Checking the prerequisites before launching the program
    """

    def __init__(self):
        print("Check prerequisites...")

    def check(self):
        """
        Check prerequisites
        """
        if self.__python_version() == 1:
            print("Python" + str(self.__python_version_int[0]) + "." + str(self.__python_version_int[1]) +
                  "." + str(self.__python_version_int[2]) + " on " + platform.system())
        else:
            print("You must run the program under Python 3 minimum!")

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

    def vbox_sdk_download(self):
        """
        Download the VBOX SDK
        :return:
        """

    def vbox_sdk_get_latest_stable_version(self):
        """
        Get latest stable version of vbox sdk
        :return:
        """
        self.__latest_stable_version = urllib.request.Request(cfg['sdk']['vbox_url_latest_stable_version'])
        with urllib.request.urlopen(self.__latest_stable_version) as response:
            self.__latest_stable_version = response.read().decode().rstrip()

        return self.__latest_stable_version

    def vbox_sdk_install(self):
        """
        TODO
        :return:
        """