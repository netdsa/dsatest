
import sys
import logging
import subprocess
import telnetlib
import re

import paramiko

logger = logging.getLogger('dsatest')


class Control(object):

    def getLastExitCode(self):
        return self.getLastExitCode

    def isConnected(self):
        raise NotImplementedError()

    def checkExitCode(self, expected_exit_code):
        actual_exit_code = self.getLastExitCode()
        if actual_exit_code != expected_exit_code:
            raise ValueError("Exit code mismatch. Got {}, expected {}".format(
                actual_exit_code, expected_exit_code))

    def _execute(self, command):
        raise NotImplementedError()

    def execute(self, command):
        """
        Wrap subclasses' execute functions with a logging facility. That way,
        logging is factorized and consistent for all of them.
        """
        class_name = self.__class__.__name__
        logger.debug("%s: Executing: %s", class_name, command)

        self.exit_code, stdout, stderr = self._execute(command)

        logger.debug("%s: Command returned %d", class_name, self.exit_code)
        if stdout != '':
            for line in stdout.split('\n'):
                logger.debug("%s: stdout: %s", class_name, line)
        if stderr != '':
            for line in stderr.split('\n'):
                logger.debug("%s: stderr: %s", class_name, line)

        return self.exit_code, stdout, stderr

    def execAndCheck(self, command, expected_exit_code=0):
        self.execute(command)
        self.checkExitCode(expected_exit_code)

    def search_for_config(self, cfg_section, options):
        """
        Search in the configParser section for the listed options. Options must
        be a dictionary. The keys will be looked up in the configuration file,
        and attributes with the same name will be assigned either the value
        found in the configuration file, or value associated with the key in
        the dictionary.
        """
        for key, default in options.items():
            val = default
            if key in cfg_section:
                val = cfg_section[key]
            setattr(self, key, val)

    @staticmethod
    def strip_variables(*args):
        """
        Strip strings from *args from leading and trailing whitespaces,
        single quote, and double quotes. That prevents some simple failures
        if ssh username or password are stored quoted in the config file.
        """
        ret = list()
        for arg in args:
            if arg is not None:
                arg = arg.strip(" '\"")
            ret.append(arg)
        return ret


class LocalControl(Control):

    def __init__(self, hostname, port, bench_parser):
        pass

    def isConnected(self):
        return True

    def _execute(self, command):
        if sys.version_info[0] >= 3:
            ret = subprocess.run(command, shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = ret.returncode
            stdout = ret.stdout.decode(sys.stdout.encoding).strip()
            stderr = ret.stderr.decode(sys.stderr.encoding).strip()
        else:
            ret = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            ret.wait()
            exit_code = ret.returncode
            stdout = ret.stdout.read().strip()
            stderr = ret.stderr.read().strip()

        return exit_code, stdout, stderr


class SSHControl(Control):

    SSH_TIMEOUT = 15

    def __init__(self, address, port, bench_parser):
        # let's search extra argument we might need
        target_section = bench_parser.config[bench_parser.TARGET_IDENTIFIER]

        options = {
            "username": "root",
            "password": None,
            "keyfile": None,
            "system_host_keys": None,
        }

        self.search_for_config(target_section, options)

        logging.getLogger("paramiko").setLevel(logging.WARNING)

        self.address = address
        self.port = port
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.load_system_host_keys(self.system_host_keys)
        self.is_connected = False


    def isConnected(self):
        return self.is_connected


    def connect(self):
        username, password, keyfile = Control.strip_variables(self.username,
                                                              self.password,
                                                              self.keyfile)
        if password is not None and keyfile is not None:
            self.ssh_client.connect(self.address, self.port, username=username,
                                    key_filename=keyfile, password=password,
                                    timeout=SSHControl.SSH_TIMEOUT)
        elif keyfile is not None:
            self.ssh_client.connect(self.address, self.port, username=username,
                                    key_filename=keyfile,
                                    timeout=SSHControl.SSH_TIMEOUT)
        elif password is not None:
            self.ssh_client.connect(self.address, self.port, username=username,
                                    password=password, look_for_keys=False,
                                    timeout=SSHControl.SSH_TIMEOUT)
        else:
            # let's try with SSH agent, hopefully key will be not encrypted
            self.ssh_client.connect(self.address, self.port, username=username,
                                    timeout=SSHControl.SSH_TIMEOUT)

        self.is_connected = True


    def disconnect(self):
        self.ssh_client.close()
        self.is_connected = False


    def _execute(self, command):
        """Execute a command on a machine, using SSH"""
        _, stdout, stderr = self.ssh_client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        stdout = stdout.read().decode().strip()
        stderr = stderr.read().decode().strip()

        return exit_code, stdout, stderr

    def getLastExitCode(self):
        return self.exit_code


class TelnetControl(Control):

    TELNET_TIMEOUT = 15

    def __init__(self, address, port, bench_parser):
        target_section = bench_parser.config[bench_parser.TARGET_IDENTIFIER]

        options = {
            "username": None,
            "password": None,
            "prompt": None,
        }

        self.search_for_config(target_section, options)

        self.address = address
        self.port = port
        self.telnet_client = telnetlib.Telnet(address)
        self.prompt = self.prompt.replace('"', '')
        self.is_connected = False


    def isConnected(self):
        return self.is_connected


    def connect(self):
        username, password = Control.strip_variables(self.username, self.password)
        self.telnet_client.open(self.address, self.port)
        if username is not None:
            self.telnet_client.read_until("login: ".encode())
            self.telnet_client.write((username + "\n").encode())
        if password is not None:
            self.telnet_client.read_until("Password: ".encode())
            self.telnet_client.write((password + "\n").encode())
        self.is_connected = True


    def disconnect(self):
        self.telnet_client.close()
        self.is_connected = False

    def _execute(self, command):
        """Execute a command on a machine, using Telnet"""
        """
        Confirm the command was correctly echoed back and then ask for
        its return code
        """
        self.telnet_client.write((command + "\r\n").encode())
        resp = self.telnet_client.read_until((command + "\r\n").encode())
        while True:
            resp = self.telnet_client.read_until(self.prompt.encode())
            if resp is not None:
                break

        stdout = resp.decode()
        stderr = ""
        self.telnet_client.write("echo $?\r\n".encode())
        _, match, _ = self.telnet_client.expect([re.compile(br'(\d+)')],
                                                TelnetControl.TELNET_TIMEOUT)
        exit_code = int(match.group(1).decode())

        if exit_code != 0:
            stderr = resp.decode()
        return exit_code, stdout, stderr
