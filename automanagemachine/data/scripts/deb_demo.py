#!/usr/bin/env python3
# coding: utf-8

import subprocess
import os
import importlib
import uuid
import tempfile

WORKDIR = os.getcwd()
URL_SSH_PUB_KEY = "https://gist.githubusercontent.com/frnode/681d838e61ff579e935eec1ac910a226/raw/OC_P5_RSA_PUB_KEY.pub"
SSH_USER = "AMM"


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
    process = subprocess.run(args, check=True, universal_newlines=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

    if process.returncode == 0:
        # TODO: Use log
        print(process.stdout)
    else:
        # TODO: Use log
        print(process.stderr)


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

# download SSH pub file and add permit key
with tempfile.TemporaryDirectory() as directory:
    print('The created temporary directory is %s' % directory)
    ssh_pub_key = wget.download(URL_SSH_PUB_KEY, directory, bar=None)
    ssh_pub_key_filename = wget.detect_filename(url=URL_SSH_PUB_KEY)

    ssh_pub_key_path = directory + "/" + ssh_pub_key_filename

    print(ssh_pub_key_path)
