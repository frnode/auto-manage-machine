#!/usr/bin/env python3
# coding: utf-8
import os
import re
import shutil
import urllib
import zipfile

from automanagemachine.components import utils
from automanagemachine.components.requirements.requirements import Requirements
from automanagemachine.core import logger, cfg


class RequirementsVboxSdk(Requirements):
    """
    Requirements for Vbox API
    """

    def verify(self):
        """
        Start pre-requisite for VBOX API
        """
        Requirements.verify(self)
        self.__verify_vbox_sdk()

    def __verify_vbox_sdk(self):
        """
        Prerequisites vbox sdk
        """
        logger.info("Starting the vbox pre-requisite check...")

        __sdk_version = cfg['sdk']['vbox_sdk']

        if __sdk_version == "latest":
            __latest_sdk_version = self.__vbox_sdk_get_latest_stable_version()
            logger.info("Starting the vbox configuration using the latest version of the SDK: " + __latest_sdk_version)
            self.__vbox_sdk_exist(__latest_sdk_version)
        else:
            __regex_test = self.__vbox_sdk_version_test_regex(__sdk_version)
            if __regex_test is None:
                logger.critical(
                    'Please check the value of "vbox_sdk" in the configuration file, it must contain 3 numbers '
                    'separated by points')
                utils.stop_program()
            elif __regex_test is not None:
                logger.debug("Validated SDK version: " + __regex_test.group())
                self.__vbox_sdk_exist(__sdk_version)

    def __vbox_sdk_version_test_regex(self, str):
        """
        Test if the version is valid
        :param str: Version text
        :return: Bool
        """
        return re.search("^\d+(\.\d+){2,2}$", str)

    def __vbox_sdk_exist(self, version):
        """
        Check if the API already exists
        """
        __sdk_dir_exist = os.path.isdir(os.getcwd() + "/vboxapi")

        if __sdk_dir_exist is False:
            logger.info('The API does not exist, launching the download and installation process...')
            file = self.__vbox_sdk_download(version)
            utils.unzip_file(file=file, to="./tmp/")
            self.__vbox_sdk_install()
        else:
            logger.info('The API already exists, let\'s continue')
            utils.stop_program()

    def __vbox_sdk_get_latest_stable_version(self):
        """
        Get latest stable version of vbox sdk
        :return: Last stable release
        """
        __url_latest_stable_version = cfg['sdk']['vbox_url_latest_stable_version']
        __latest_stable_version = urllib.request.Request(__url_latest_stable_version)
        with urllib.request.urlopen(__latest_stable_version) as response:
            __latest_stable_version = response.read().decode().rstrip()

        __regex_test = self.__vbox_sdk_version_test_regex(__latest_stable_version)

        if __regex_test is None:
            logger.critical(
                'The value of the version does not match the regex, it must contain 3 numbers separated by points. '
                'Check with the following URL: ' + __url_latest_stable_version)
            utils.stop_program()

        return __latest_stable_version

    def __vbox_sdk_download(self, version):
        """
        Download VBOX SDK
        :param version: Specify version download
        :return: Path of the downloaded file
        """
        logger.info("Starting the download process...")

        __tmp_directory = os.getcwd() + "/tmp"
        __vbox_sdk_url_repo = cfg['sdk']['vbox_url_repo'] + version + "/"
        __vbox_sdk_url_repo_index_html = __vbox_sdk_url_repo + "index.html"

        try:
            __vbox_sdk_url_repo_read_index = urllib.request.urlopen(__vbox_sdk_url_repo_index_html).read()
        except urllib.error.URLError as e:
            __text_error = "Can not access the following URL: " + __vbox_sdk_url_repo_index_html
            logger.critical(__text_error)
            utils.stop_program()
        except urllib.error.HTTPError as e:
            __text_error = "Can not access the following URL: " + __vbox_sdk_url_repo_index_html + " (HTTPError code: " \
                           + str(e.code) + ")"
            logger.critical(__text_error)
            utils.stop_program()

        __vbox_sdk_url_download_search = re.search(b'(VirtualBoxSDK-)(.*?)(zip)', __vbox_sdk_url_repo_read_index)

        if __vbox_sdk_url_download_search is None:
            __text_error = "Can not find SDK download link"
            logger.critical(__text_error)
            utils.stop_program()

        __vbox_sdk_url_download = __vbox_sdk_url_download_search.group().decode()
        __url_download = __vbox_sdk_url_repo + __vbox_sdk_url_download

        logger.debug("Check if the directory (" + __tmp_directory + ") already exists")

        if os.path.isdir(__tmp_directory) is False:
            os.mkdir(__tmp_directory)
            logger.debug("Directory '" + __tmp_directory + "' created")
        else:
            logger.debug("Directory '" + __tmp_directory + "' already exists")

        logger.info("Downloading the " + __url_download + " file in progress...")

        try:
            file = urllib.request.urlretrieve(__url_download, __tmp_directory + "/" + __vbox_sdk_url_download)
        except urllib.error.URLError as e:
            __text_error = "Can not access the following URL: " + __url_download
            logger.critical(__text_error)
            utils.stop_program()
        except urllib.error.HTTPError as e:
            __text_error = "Can not access the following URL: " + __url_download + " (HTTPError code: " \
                           + str(e.code) + ")"
            logger.critical(__text_error)
        except urllib.error.ContentTooShortError as e:
            __text_error = "There was a problem downloading the file"
            logger.critical(__text_error)
            utils.stop_program()

        logger.info("The file has been downloaded")

        return file[0]

    def __vbox_sdk_install(self):
        """
        Installing the VBOX API
        :rtype: object
        """
        __path_script = os.getcwd() + "/tmp/sdk/installer/"
        __path_script_final = __path_script + "vboxapisetup.py install"
        utils.run_python_script(__path_script_final, path_to_run=__path_script)

        __source_directory = __path_script + "build/lib/vboxapi"
        __dest_directory = os.getcwd() + '/vboxapi/'

        __vboxapi_directory = os.getcwd() + "/vboxapi"

        logger.info("Check if the " + __vboxapi_directory + " folder exists...")

        if os.path.isdir(__vboxapi_directory) is True:
            logger.warning("Deleting the folder: " + __vboxapi_directory)
            try:
                shutil.rmtree(__vboxapi_directory)
            except shutil.Error as e:
                logger.warning("Can remove the folder: " + __vboxapi_directory)

        try:
            shutil.move(__source_directory, __dest_directory)
        except shutil.Error as e:
            logger.warning("Can not move the folder: " + __source_directory + " to " + __dest_directory)

        __tmp_folder = os.getcwd() + "/tmp"
        try:
            shutil.rmtree(__tmp_folder)
        except shutil.Error as e:
            logger.warning("Can remove the folder: " + __tmp_folder)

        logger.info("The VBOX API has been successfully installed: " + __dest_directory)
