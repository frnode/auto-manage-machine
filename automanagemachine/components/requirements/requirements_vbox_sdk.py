#!/usr/bin/env python3
# coding: utf-8
import os
import re
import shutil
import urllib.request
import urllib.response

from automanagemachine.components import utils
from automanagemachine.core import logger, cfg
from automanagemachine.components.requirements.requirements import Requirements


class RequirementsVboxSdk(Requirements):
    """
    Requirements for Vbox API
    """

    def __init__(self):
        Requirements.__init__(self)
        logger.info("Starting the vbox pre-requisite check...")
        self.sdk_version = cfg['sdk']['vbox_sdk']
        self.sdk_url_latest_stable_version = cfg['sdk']['vbox_url_latest_stable_version']
        self.sdk_latest_stable_version = None
        self.tmp_directory = os.getcwd() + "/tmp"
        self.sdk_directory = os.getcwd() + "/vboxapi"
        self.run()

    def run(self):
        """
        Run process requirements for VBOX
        """
        self.verify()

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
        if self.sdk_version == "latest":
            self.sdk_latest_stable_version = self.__vbox_sdk_get_latest_stable_version()
            logger.info("Starting the vbox configuration using the latest version of the SDK: " +
                        self.sdk_latest_stable_version)
            self.__vbox_sdk_exist(self.sdk_latest_stable_version)
        else:
            __regex_test = self.__vbox_sdk_version_test_regex(self.sdk_version)
            if __regex_test is None:
                logger.critical(
                    'Please check the value of "vbox_sdk" in the configuration file, it must contain 3 numbers '
                    'separated by points')
                utils.stop_program()
            elif __regex_test is not None:
                logger.debug("Validated SDK version: " + __regex_test.group())
                self.__vbox_sdk_exist(self.sdk_version)

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
        __sdk_dir_exist = os.path.isdir(self.sdk_directory)

        if __sdk_dir_exist is False:
            logger.info('The API does not exist, launching the download and installation process...')
            __file = self.__vbox_sdk_download(version)
            utils.unzip_file(file=__file, to="./tmp/")
            self.__vbox_sdk_install()
        else:
            logger.info('The API already exists, let\'s continue')

    def __vbox_sdk_get_latest_stable_version(self):
        """
        Get latest stable version of vbox sdk
        :return: Last stable release
        """
        __latest_stable_version_request = urllib.request.Request(self.sdk_url_latest_stable_version)
        with urllib.request.urlopen(__latest_stable_version_request) as response:
            __latest_stable_version_response = response.read().decode().rstrip()

        __regex_test = self.__vbox_sdk_version_test_regex(__latest_stable_version_response)

        if __regex_test is None:
            logger.critical(
                'The value of the version does not match the regex, it must contain 3 numbers separated by points. '
                'Check with the following URL: ' + self.sdk_url_latest_stable_version)
            utils.stop_program()

        return __latest_stable_version_response

    def __vbox_sdk_download(self, version):
        """
        Download VBOX SDK
        :param version: Specify version download
        :return: Path of the downloaded file
        """
        logger.info("Starting the download process...")

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

        logger.debug("Check if the directory (" + self.tmp_directory + ") already exists")

        if os.path.isdir(self.tmp_directory) is False:
            os.mkdir(self.tmp_directory)
            logger.debug("Directory '" + self.tmp_directory + "' created")
        else:
            logger.debug("Directory '" + self.tmp_directory + "' already exists")

        logger.info("Downloading the " + __url_download + " file in progress...")

        try:
            __file = urllib.request.urlretrieve(__url_download, self.tmp_directory + "/" + __vbox_sdk_url_download)
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

        return __file[0]

    def __vbox_sdk_install(self):
        """
        Installing the VBOX API
        :rtype: object
        """
        __path_script = os.getcwd() + "/tmp/sdk/installer/"
        __path_script_final = __path_script + "vboxapisetup.py install"

        utils.run_python_script(__path_script_final, path_to_run=__path_script)

        __source_directory = __path_script + "build/lib/vboxapi"
        __vboxapi_directory = self.sdk_directory
        __dest_directory = __vboxapi_directory + "/"

        logger.info("Check if the " + __vboxapi_directory + " folder exists...")

        if os.path.isdir(__vboxapi_directory) is True:
            logger.warning("Deleting the folder: " + __vboxapi_directory)
            try:
                shutil.rmtree(__vboxapi_directory)
            except shutil.Error:
                logger.warning("Can remove the folder: " + __vboxapi_directory)

        try:
            shutil.move(__source_directory, __dest_directory)
        except shutil.Error:
            logger.warning("Can not move the folder: " + __source_directory + " to " + __dest_directory)

        try:
            shutil.rmtree(self.tmp_directory)
        except shutil.Error:
            logger.warning("Can remove the folder: " + self.tmp_directory)

        logger.info("The VBOX API has been successfully installed: " + __dest_directory)
