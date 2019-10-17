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

import glob
import os
import platform
import re
import shutil
import stat
import urllib.request
import urllib.response

from automanagemachine.components import utils
from automanagemachine.core import logger, cfg, cfg_vbox, MODULE_DIR
from automanagemachine.components.requirements.requirements import Requirements


class RequirementsVboxSdk(Requirements):
    """
    Requirements for Vbox API
    """

    def __init__(self):
        Requirements.__init__(self)
        logger.info("Starting the vbox pre-requisite check...")
        self.sdk_version = cfg_vbox['sdk_virtualbox']['vbox_sdk']
        self.sdk_url_latest_stable_version = cfg_vbox['sdk_virtualbox']['vbox_url_latest_stable_version']
        self.sdk_latest_stable_version = None
        self.tmp_directory = MODULE_DIR + "tmp"
        self.sdk_directory = MODULE_DIR + "vboxapi"
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
        if self.sdk_version.lower() == "latest":  # If the last one was set in the configuration
            self.sdk_latest_stable_version = self.__vbox_sdk_get_latest_stable_version()
            self.sdk_version = self.sdk_latest_stable_version
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

        if __sdk_dir_exist:  # Check if the "vboxapi" folder exists
            __file_version = self.sdk_directory + "/" + "version.txt"
            if os.path.exists(__file_version):  # Check if the "version.txt" file exists
                logger.info("Check if the version that exists is equal to the version of the configuration file")
                with open(__file_version, 'rb') as f:
                    try:
                        __version_vbox_sdk = f.read().decode("utf8")
                    except:
                        logger.info("Can not read the file: " + __file_version)
                        utils.stop_program()

                # Check if the version that exists is equal to the version of the configuration file
                if __version_vbox_sdk != version:
                    try:
                        shutil.rmtree(self.sdk_directory)  # Delete the folder
                    except shutil.Error:
                        logger.warning("Can remove the folder: " + self.sdk_directory)
                    finally:
                        return self.__vbox_sdk_exist(
                            version)  # Restart the process to download the requested version

            logger.info('The API already exists, let\'s continue')
        else:
            logger.info('The API does not exist, launching the download and installation process...')
            __file_zip_sdk = self.__vbox_sdk_download(version)
            self.__vbox_sdk_install(__file_zip_sdk)

    def __vbox_sdk_get_latest_stable_version(self):
        """
        Get latest stable version of vbox sdk
        :return: Last stable release, retrieved from the internet
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

        __vbox_sdk_url_repo = cfg_vbox['sdk_virtualbox']['vbox_url_repo'] + version + "/"
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

        if os.path.isdir(self.tmp_directory):
            logger.debug("Directory '" + self.tmp_directory + "' already exists")
        else:
            os.mkdir(self.tmp_directory, 0o777)
            logger.debug("Directory '" + self.tmp_directory + "' created")

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

    def __vbox_sdk_install(self, file_zip_sdk):
        """
        Installing the VBOX API
        """
        utils.unzip_file(file=file_zip_sdk, to=MODULE_DIR + "tmp/")  # Unzip the file

        __path_script = MODULE_DIR + "tmp/sdk/installer/"
        __path_script_final = __path_script + "vboxapisetup.py install"
        __source_directory = __path_script + "build/lib/vboxapi/"

        # Set permissions
        for root, dirs, files in os.walk(MODULE_DIR + "tmp/"):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o755)
            for f in files:
                os.chmod(os.path.join(root, f), 0o755)

        # Launch the vbox SDK installation script
        if platform.system() == "Windows":
            # Windows support
            utils.run_python_script(__path_script_final, path_to_run=__path_script)
        else:
            # TODO: Linux support
            utils.run_python_script("python " + __path_script_final, path_to_run=__path_script)

        __vboxapi_directory = self.sdk_directory
        __dest_directory = __vboxapi_directory + "/"

        logger.info("Check if the " + __vboxapi_directory + " folder exists...")

        if os.path.isdir(__vboxapi_directory):
            logger.warning("Deleting the folder: " + __vboxapi_directory)
            try:
                shutil.rmtree(__vboxapi_directory)
            except (shutil.Error, FileNotFoundError):
                logger.warning("Can remove the folder: " + __vboxapi_directory)

        os.mkdir(__dest_directory)
        logger.debug("Directory '" + __dest_directory + "' created")

        try:
            files = os.listdir(__source_directory)
            for f in files:
                shutil.move(__source_directory + f, __dest_directory)
        except (shutil.Error, FileNotFoundError, PermissionError):
            logger.warning("Can not move the folder: " + __source_directory + " to " + __dest_directory)

        try:
            shutil.rmtree(self.tmp_directory)
        except (shutil.Error, FileNotFoundError, PermissionError):
            logger.warning("Can remove the folder: " + self.tmp_directory)

        logger.info("Creating the file containing the SDK version")

        try:
            # Create the "version.txt" file containing the version number downloaded
            with open(__dest_directory + "version.txt", "w") as outfile:
                outfile.write(self.sdk_version)

            logger.info("Created file: version.txt")
        except IOError:
            logger.warning("Could not create version.txt file")
            utils.stop_program()

        logger.info("The VBOX API has been successfully installed: " + __dest_directory)
