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

import subprocess
import os
import importlib
import sys
import uuid
import tempfile
import re

WORKDIR = os.getcwd()  # DON'T TOUCH

# CONFIGURATION
URL_SSH_PUB_KEY = "https://gist.githubusercontent.com/frnode/681d838e61ff579e935eec1ac910a226/raw/OC_P5_RSA_PUB_KEY.pub"  # SSH key URL
SSH_USER = "amm"  # Name of the user to create
DOMAIN = SSH_USER  # domain name, without "http(s)"


def super_pip(packages, retry=False):
    """
    Install the defined pip packages
    :param packages: List of packages to install
    :param retry: True: If the function is started from itself
    """
    import pip

    if retry:
        print_console("Import pip package: " + packages)
        globals()[packages] = importlib.import_module(packages)
    else:
        for package in packages:
            print_console("Install/import pip package: " + package)
            try:
                globals()[package] = importlib.import_module(package)
            except ImportError:
                if hasattr(pip, 'main'):
                    pip.main(['install', package])
                else:
                    pip._internal.main(['install', package])

                super_pip(package, retry=True)


def subprocess_run(args, wait=True):
    """
    Run command and return stdout or strerr
    :param wait: Wait
    :param args: List containing the command and arguments
    :return: Return code
    """
    try:
        p = subprocess.Popen(
            args,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if wait:
            p.wait()

        stdout, stderr = p.communicate()
    except subprocess.CalledProcessError as e:
        lines = stderr.decode('utf-8').splitlines()
        for line in lines:
            line = remove_specials_characters(line)
            print(line, file=sys.stderr)

    if p.returncode == 0:
        lines = stdout.decode('utf-8').splitlines()
        for line in lines:
            line = remove_specials_characters(line)
            print(line, file=sys.stdout)

    return p.returncode


def remove_specials_characters(str):
    """
    Remove annoying characters for display in the console
    :param str: Character string to clean
    :return: Character string cleaned
    """
    str = re.sub(r"[^a-zA-Z0-9 .,/()<>+=@%!\"#?'~$^&*:;[\]_\\-]", ' ', str)
    return str


def print_console(text):
    print("*::: " + text + " :::*")


def generate_random_str(length=6):
    """
    Generate a string of random characters
    :param length: Length of the string
    :return: String of characters
    """
    return uuid.uuid4().hex[:length].upper()


class User:
    """
    Manage the user
    """

    def __init__(self, user, password=None):
        self.user = user
        self.password = password

    def create(self):
        """
        Create a user
        """
        import pwd

        try:
            pwd.getpwnam(self.user)
        except KeyError:
            print_console("User creation: " + self.user)
            __params = ["adduser"]

            # If the password is blank, disable it
            if not self.password:
                __params.append("--disabled-password")

            __params.append("--gecos")
            __params.append("")
            __params.append("--home")
            __params.append("/home/" + self.user)
            __params.append(self.user)

            subprocess_run(__params)


class SSHAuthorizedKeys:
    """
    Manage SSH keys
    """

    def __init__(self, user, key_url):
        self.user = user
        self.key_url = key_url
        self.key_path_user = None

    def create_dir_and_file(self):
        """
        Create the directories and files needed to authorize the key
        """
        if self.user == "root":
            __directory = "/" + self.user + "/.ssh/"
        else:
            __directory = "/home/" + self.user + "/.ssh/"

        if not os.path.exists(__directory):
            print_console("Creating the folder: " + __directory)
            os.makedirs(__directory, 0o700, exist_ok=True)

        __authorized_keys_file = __directory + "authorized_keys"
        __file_exists = os.path.isfile(__authorized_keys_file)

        if not __file_exists:
            print_console("Creating the file: " + __authorized_keys_file)
            open(__authorized_keys_file, "w")

        print_console("Define rights")
        os.chmod(__authorized_keys_file, 0o600)
        subprocess_run(["chown", self.user + ":" + self.user, __directory])
        subprocess_run(["chown", self.user + ":" + self.user, __authorized_keys_file])

        self.key_path_user = __authorized_keys_file

    def authorize_key(self):
        """
        Create a temporary directory to download the key and use it in the created file.
        :return: Path of the file containing the key
        """
        with tempfile.TemporaryDirectory() as directory:
            print("The created temporary directory is" + directory)
            __ssh_pub_key_filename = self.__download_key(directory)
            __ssh_pub_key_path = directory + "/" + __ssh_pub_key_filename
            __ssh_key_str = self.read_file(__ssh_pub_key_path)

            print_console("Allow the key: " + __ssh_key_str)
            self.put_key(self.key_path_user, __ssh_key_str)
            return __ssh_pub_key_path

    def __download_key(self, directory):
        """
        Download the key from a defined URL and place it in the folder and return the file name.
        :param directory: File where the file containing the key should be placed
        :return: Name of the file containing the key
        """
        print_console("Downloading the key: " + self.key_url + " in the folder:" + directory)
        wget.download(self.key_url, directory, bar=None)
        __ssh_pub_key_filename = wget.detect_filename(url=self.key_url)
        return __ssh_pub_key_filename

    def read_file(self, file):
        """
        Read a file
        :param file: File to read
        :return: File contents
        """
        with open(file, 'r') as filehandle:
            return filehandle.read()

    def put_key(self, to_file, key_str):
        """
        Write the key in a file
        :param to_file: File where the key should be written
        :param key_str: Key to be written
        """
        with open(to_file, "a") as file:
            file.write("\n" + key_str)

    def configure_sshd_config(self):
        """
        Configure the ssh to be able to connect using our private key
        """
        print_console("Setting the SSH configuration")

        with open("/etc/ssh/sshd_config", 'r+') as f:
            data = f.read()
            data = re.sub(r'(^[#\s]*PubkeyAuthentication.*$)', r'PubkeyAuthentication yes', data, flags=re.MULTILINE)
            data = re.sub(r'(^[#\s]*PermitEmptyPasswords.*$)', r'PermitEmptyPasswords no', data, flags=re.MULTILINE)
            data = re.sub(r'(^[#\s]*PasswordAuthentication.*$)', r'PasswordAuthentication no', data,
                          flags=re.MULTILINE)
            data = re.sub(r'(^[#\s]*PermitRootLogin.*$)', r'PermitRootLogin no', data, flags=re.MULTILINE)
            f.seek(0)
            f.truncate()
            f.write(data)

        self.restart_sshd()

    def restart_sshd(self):
        """
        Restart ssh service
        """
        print_console("Restarting the ssh service")
        subprocess_run(["service", "ssh", "restart"])


class Apache2:
    """
    Manage Apache2
    """

    def __init__(self, user):
        self.user = user
        self.user_www_dir = None
        self.domain = user
        self.document_root = "/home/" + self.user + "/public_html"

    def install(self):
        """
        Install Apache2
        """
        print_console("Installing apache2")
        return subprocess_run(["apt-get", "-y", "install", "apache2"])

    def reload(self):
        """
        Reload Apache2 configurations
        """
        print_console("Reloading the apache2 configuration")
        return subprocess_run(["service", "apache2", "reload"])

    def enable_conf(self, name):
        """
        Enables an Apache2 configuration
        :param name: Name of the configuration to activate
        """
        print_console("Enabling vhost: " + name + ".conf")
        return subprocess_run(["a2ensite", name + ".conf"])

    def __create_dir(self):
        """
        Define the path containing the site's files, create it if it does not exist
        :return: Folder path containing the site files
        """
        if self.user == "root":
            self.document_root = "/var/www/html"
        else:
            self.document_root = "/home/" + self.user + "/public_html"

        # Create the folder if it does not exist
        if not os.path.exists(self.document_root):
            print_console("Creating the folder: " + self.document_root)
            os.makedirs(self.document_root, 0o750, exist_ok=True)

        return self.document_root

    def __set_permissions(self, folder):
        """
        Set permissions on the folder
        :param folder: Folder containing the site files
        """
        print_console("Set rights on the folder: " + folder)
        subprocess_run(["chown", "-R", self.user + ":www-data", folder])
        subprocess_run(["chmod", "750", "-R", folder])

    def put_default_index(self):
        """
        Create an index.html file that contains default content
        """
        print_console("Creating the default index.html file")
        __index_html = """<!doctype html>
                <html lang="fr">
                <head>
                  <meta charset="utf-8">
                  <title>OCP6 - %s</title>
                </head>
                <body>
                <center><h1 style="color:#7451EB;">Welcome to the <b>%s</b> website</h1></center>
                </p>
                <center>
                <h5><b>OCP6</b></h5>
                <img src="https://openclassrooms.com/fav-icon.png?v=3"></center>
                </body>
                </html>""" % (self.domain, self.domain)

        __index_html_file = self.document_root + "/index.html"
        with open(__index_html_file, "w") as file:
            file.write(__index_html)

    def create_vhost(self, domain, folder):
        """
        Write the vhost file with the defined parameters
        """
        print_console("Creation of the vhost: " + domain + ".conf")
        __virtual_host = """<VirtualHost *:80>
            ServerAdmin admin@%s
            ServerName %s
            ServerAlias www.%s
            DocumentRoot %s

            ErrorLog ${APACHE_LOG_DIR}/error.log
            CustomLog ${APACHE_LOG_DIR}/access.log combined

            <Directory %s>
                DirectoryIndex index.html
                <Limit POST GET OPTIONS>
                    Require all granted
                </Limit>
                <LimitExcept POST GET OPTIONS>
                    Require all denied
                </LimitExcept>
            </Directory>
        </VirtualHost>
                """ % (domain, domain, domain, folder, folder)

        __conf_file = "/etc/apache2/sites-available/" + domain + ".conf"
        with open(__conf_file, "w") as file:
            file.write(__virtual_host)

    def create(self, domain):
        """
        Create the necessary to host the files of the site
        :param domain: Domain name
        """
        self.domain = domain
        __document_root = self.__create_dir()
        self.put_default_index()
        self.__set_permissions(__document_root)
        self.create_vhost(domain, __document_root)
        self.enable_conf(domain)
        self.reload()


print_console("START OF SCRIPT")
subprocess_run(["apt-get", "update"])
subprocess_run(["apt-get", "-y", "install", "python3-pip"])

super_pip(['wget', 'ifaddr'])  # pip install wget

user = User(SSH_USER, None)
user.create()

ssh = SSHAuthorizedKeys(user.user, URL_SSH_PUB_KEY)
ssh.create_dir_and_file()
ssh.authorize_key()
ssh.configure_sshd_config()

apache = Apache2(user.user)
apache.install()
apache.create(DOMAIN)

print_console("END OF THE SCRIPT")
print_console("Machine information")
print("* Network interfaces: ")
adapters = ifaddr.get_adapters()
for adapter in adapters:
    print(adapter.nice_name)
    for ip in adapter.ips:
        print("   %s/%s" % (ip.ip, ip.network_prefix))

print_console("SSH")
print("* Session name: " + user.user)
print("* Use your private key to connect")
print_console("WEB")
print("* Link created web space: " + DOMAIN)
