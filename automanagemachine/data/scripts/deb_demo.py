#!/usr/bin/env python3
# coding: utf-8

import subprocess
import os
import importlib
import uuid
import tempfile

WORKDIR = os.getcwd()
URL_SSH_PUB_KEY = "https://gist.githubusercontent.com/frnode/681d838e61ff579e935eec1ac910a226/raw/OC_P5_RSA_PUB_KEY.pub"
SSH_USER = "amm2"


def super_pip(packages):
    """
    TODO
    :param packages:
    """
    import pip
    for package in packages:
        try:
            globals()[package] = importlib.import_module(package)
        except ImportError:
            if hasattr(pip, 'main'):
                pip.main(['install', package])
            else:
                pip._internal.main(['install', package])

            super_pip(package)


def subprocess_run(args):
    """
    Run command and return Stdout or Strerr
    """
    try:
        process = subprocess.run(args, check=True, universal_newlines=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
    else:
        if process.returncode == 0:
            # TODO: Use log
            print(process.stdout)


def generate_random_str(length=6):
    """
    Generate a string of random characters
    :param length: Length of the string
    :return: String of characters
    """
    return uuid.uuid4().hex[:length].upper()


subprocess_run(["apt-get", "update"])
subprocess_run(["apt-get", "-y", "install", "python3-pip"])

super_pip(['wget'])  # pip install wget


class User:
    """
    TODO
    """

    def __init__(self, user, password=None):
        self.user = user
        self.password = password
        pass

    def create(self):
        """
        TODO
        """
        __params = ["adduser"]

        # If the password is blank, disable it
        if not self.password:
            __params.append("--disabled-password")

        __params.append("--gecos")
        __params.append("")
        __params.append(self.user)

        subprocess_run(__params)


class SSHAuthorizedKeys:
    """
    TODO
    """

    def __init__(self, user, key_url):
        self.user = user
        self.key_url = key_url
        self.key_path_user = None

    def create_dir_and_file(self):
        """
        TODO
        """
        __directory = "/home/" + self.user + "/.ssh/"

        if not os.path.exists(__directory):
            os.makedirs(__directory)

        __authorized_keys_file = __directory + "authorized_keys"
        __file_exists = os.path.isfile(__authorized_keys_file)
        if not __file_exists:
            open(__authorized_keys_file, "w")

        self.key_path_user = __authorized_keys_file

    def authorize_key(self):
        """
        TODO
        :return:
        """
        with tempfile.TemporaryDirectory() as directory:
            __ssh_pub_key_filename = self.__download_key(directory)
            __ssh_pub_key_path = directory + "/" + __ssh_pub_key_filename

            __ssh_key_str = self.read_file(__ssh_pub_key_path)
            self.put_key(self.key_path_user, __ssh_key_str)
            return __ssh_pub_key_path

    def __download_key(self, directory):
        """
        TODO
        :param directory:
        :return:
        """
        print('The created temporary directory is %s' % directory)
        wget.download(self.key_url, directory, bar=None)
        __ssh_pub_key_filename = wget.detect_filename(url=self.key_url)

        return __ssh_pub_key_filename

    def read_file(self, file):
        """
        TODO
        :param file:
        :return:
        """
        with open(file, 'r') as filehandle:
            filecontent = filehandle.read()
            return filecontent

    def put_key(self, to_file, key_str):
        """
        TODO
        :param to_file:
        :param key_str:
        """
        with open(to_file, "a") as file:
            file.write("\n" + key_str)

    def configure_ssh_config(self):
        """
        TODO
        """
        subprocess_run(["sed", "-i", "s/#\\?\\(PubkeyAuthentication\\s*\\).*$/\\1yes/", "/etc/ssh/sshd_config"])
        subprocess_run(["sed", "-i", "s/#\\?\\(PermitEmptyPasswords\\s*\\).*$/\\1no/", "/etc/ssh/sshd_config"])
        subprocess_run(["sed", "-i", "s/#\\?\\(PasswordAuthentication\\s*\\).*$/\\1no/", "/etc/ssh/sshd_config"])

    def restart_sshd(self):
        """
        TODO
        """
        subprocess_run(["service", "ssh", "restart"])


test_usr = User(SSH_USER, None)
test_usr.create()

test = SSHAuthorizedKeys(test_usr.user, URL_SSH_PUB_KEY)
test.create_dir_and_file()
test.authorize_key()
test.configure_ssh_config()
test.restart_sshd()
