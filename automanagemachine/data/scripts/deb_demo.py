#!/usr/bin/env python3
# coding: utf-8

import subprocess
import os
import importlib
import uuid
import tempfile
import re

WORKDIR = os.getcwd()
URL_SSH_PUB_KEY = "https://gist.githubusercontent.com/frnode/681d838e61ff579e935eec1ac910a226/raw/OC_P5_RSA_PUB_KEY.pub"
SSH_USER = "amm2"


def super_pip(packages, retry=False):
    """
    TODO
    :param retry:
    :param packages:
    """
    import pip

    if retry:
        globals()[packages] = importlib.import_module(packages)
    else:
        for package in packages:
            try:
                globals()[package] = importlib.import_module(package)
            except ImportError:
                if hasattr(pip, 'main'):
                    pip.main(['install', package])
                else:
                    pip._internal.main(['install', package])

                super_pip(package, retry=True)


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

    return process.returncode


def generate_random_str(length=6):
    """
    Generate a string of random characters
    :param length: Length of the string
    :return: String of characters
    """
    return uuid.uuid4().hex[:length].upper()


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
        import pwd

        try:
            pwd.getpwnam(self.user)
        except KeyError:
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
        if self.user == "root":
            __directory = "/" + self.user + "/.ssh/"
        else:
            __directory = "/home/" + self.user + "/.ssh/"

        if not os.path.exists(__directory):
            os.makedirs(__directory, 0o700, exist_ok=True)

        __authorized_keys_file = __directory + "authorized_keys"
        __file_exists = os.path.isfile(__authorized_keys_file)
        if not __file_exists:
            open(__authorized_keys_file, "w")

        os.chmod(__authorized_keys_file, 0o600)
        subprocess_run(["chown", self.user + ":" + self.user, __directory])
        subprocess_run(["chown", self.user + ":" + self.user, __authorized_keys_file])

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
            return filehandle.read()

    def put_key(self, to_file, key_str):
        """
        TODO
        :param to_file:
        :param key_str:
        """
        with open(to_file, "a") as file:
            file.write("\n" + key_str)

    def configure_sshd_config(self):
        """
        TODO
        """
        with open("/etc/ssh/sshd_config", 'r+') as f:
            data = f.read()
            data = re.sub(r'(^[#\s]*PubkeyAuthentication.*$)', r'PubkeyAuthentication yes', data, flags=re.MULTILINE)
            data = re.sub(r'(^[#\s]*PermitEmptyPasswords.*$)', r'PermitEmptyPasswords no', data, flags=re.MULTILINE)
            data = re.sub(r'(^[#\s]*PasswordAuthentication.*$)', r'PasswordAuthentication yes', data,
                          flags=re.MULTILINE)
            data = re.sub(r'(^[#\s]*PermitRootLogin.*$)', r'PermitRootLogin yes', data, flags=re.MULTILINE)
            f.seek(0)
            f.truncate()
            f.write(data)
        # TODO: PasswordAuthentication yes and PermitRootLogin yes just for DEBUG
        self.restart_sshd()

    def restart_sshd(self):
        """
        TODO
        """
        subprocess_run(["service", "ssh", "restart"])


class Apache2:
    """
    TODO
    """

    def __init__(self, user):
        self.user = user
        self.user_www_dir = None

    def create(self, domain):

        if self.user == "root":
            __document_root = "/var/www/html"
        else:
            __document_root = "/home/" + self.user + "/public_html"

        if not os.path.exists(__document_root):
            os.makedirs(__document_root, 0o750, exist_ok=True)

        subprocess_run(["chown", "-R", self.user + ":www-data", __document_root])
        # subprocess_run(["usermod", "-a", "-G", "www-data", self.user])
        subprocess_run(["chmod", "750", "-R", __document_root])

        os.system("""echo "<VirtualHost *:80>
    ServerAdmin """ + domain + """
    ServerName """ + domain + """
    ServerAlias www.""" + domain + """
    DocumentRoot """ + __document_root + """
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
    <Directory """ + __document_root + """>
    DirectoryIndex index.html
    <Limit POST GET OPTIONS>
    Require all granted
    </Limit>
    <LimitExcept POST GET OPTIONS>
    Require all denied
    </LimitExcept>
    </Directory>
</VirtualHost>" >> /etc/apache2/sites-available/""" + domain + """.conf
        """)

        subprocess_run(["a2ensite", domain + ".conf"])
        subprocess_run(["service", "apache2", "reload"])


subprocess_run(["apt-get", "update"])
subprocess_run(["apt-get", "-y", "install", "python3-pip"])

super_pip(['wget'])  # pip install wget

test_usr = User(SSH_USER, None)
test_usr.create()

test_ssh = SSHAuthorizedKeys(test_usr.user, URL_SSH_PUB_KEY)
test_ssh.create_dir_and_file()
test_ssh.authorize_key()
test_ssh.configure_sshd_config()

subprocess_run(["apt-get", "-y", "install", "apache2"])

test_apache = Apache2(test_usr.user)
test_apache.create(test_usr.user)
