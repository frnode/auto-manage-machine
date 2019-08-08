#!/usr/bin/env python3
# coding: utf-8
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import urllib.request
import re
import importlib
import zipfile
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
            return 1  # return 1 if it's ok (Python 3)
        else:
            return 0

    def vbox_sdk(self):
        """
        Download the VBOX SDK
        :return:
        """
        if cfg['sdk']['vbox_sdk'] == "latest":
            print('check or download latest version vbox sdk')
            self.__vbox_sdk_exist(self.vbox_sdk_get_latest_stable_version())
            # print("VBOX SDK: " + self.vbox_sdk_get_latest_stable_version())
        else:
            sdk_version = cfg['sdk']['vbox_sdk']
            __regex_test = re.search("^\d+(\.\d+){2,2}$", sdk_version)
            if __regex_test is None:
                print('Please check the value of "vbox_sdk" in the configuration file, it must contain 3 numbers '
                      'separated by points.')
            # TODO: Exception, stop program
            elif __regex_test is not None:
                self.__vbox_sdk_exist(sdk_version)
                print("VBOX SDK: " + __regex_test.group())

    def __vbox_sdk_exist(self, version):
        """
        TODO
        :return:
        """
        sdk_dir_exist = os.path.isdir(os.getcwd() + "/vboxapi")
        if sdk_dir_exist is False:
            file = self.__vbox_sdk_download(version)
            self.__unzip_file(file)
            self.__vbox_sdk_install()

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

    def __vbox_sdk_download(self, version):
        """
        TODO
        :return:
        """

        tmp_directory = os.getcwd() + "/tmp"
        __url = "https://download.virtualbox.org/virtualbox/" + version + "/"
        __html = urllib.request.urlopen(__url + "/index.html").read()
        __link = re.search(b'(VirtualBoxSDK-)(.*?)(zip)', __html)
        __link = __link.group().decode()

        __url_download = __url + __link

        if os.path.isdir(tmp_directory) is False:
            os.mkdir(tmp_directory)

        file = urllib.request.urlretrieve(__url_download, tmp_directory + "/" + __link)
        # # print(file[0])
        return file[0]
        #

    def run_python_script(self, command, path_to_run=os.getcwd()):
        """
        TODO
        :param path_to_run:
        :param command:
        """
        current_dir = os.getcwd()
        os.chdir(path_to_run)
        os.system(command)
        os.chdir(current_dir)
        # TODO: Exception

    def __unzip_file(self, file):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall("./tmp/")

    def __vbox_sdk_install(self):
        """
        TODO
        :return:
        """
        path_script = os.getcwd() + "/tmp/sdk/installer/"
        path_script_final = path_script + "vboxapisetup.py install"
        self.run_python_script(path_script_final, path_script)

        source_directory = path_script + "build/lib/vboxapi"
        dest_directory = os.getcwd() + '/vboxapi/'

        vboxapi_directory = os.getcwd() + "/vboxapi"
        if os.path.isdir(vboxapi_directory) is True:
            shutil.rmtree(vboxapi_directory)

        shutil.move(source_directory, dest_directory)
        shutil.rmtree(os.getcwd() + "/tmp")
