
import sys
import logging
import subprocess

import paramiko
import telnetlib
import re

logger = logging.getLogger('dsatest')


class Control(object):

    def execute(self):
        raise NotImplementedError()

    def getLastExitCode(self):
        raise NotImplementedError()

    def isConnected(self):
        raise NotImplementedError()

    def checkExitCode(self, expected_exit_code):
        actual_exit_code = self.getLastExitCode()
        if actual_exit_code != expected_exit_code:
            raise ValueError("Exit code mismatch. Got {}, expected {}".format(
                actual_exit_code, expected_exit_code))

    def execAndCheck(self, command, expected_exit_code=0):
        self.execute(command)
        self.checkExitCode(expected_exit_code)


class LocalControl(Control):

    def __init__(self, hostname, port, bench_parser):
        pass

    def isConnected(self):
        return True

    def execute(self, command):
        logger.debug("LocalControl: Executing: {}".format(command))
        if sys.version_info[0] >= 3:
            ret = subprocess.run(command, shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.exit_code = ret.returncode
            stdout = ret.stdout.decode(sys.stdout.encoding).strip()
            stderr = ret.stderr.decode(sys.stderr.encoding).strip()
        else:
            ret = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            ret.wait()
            self.exit_code = ret.returncode
            stdout = ret.stdout.read().strip()
            stderr = ret.stderr.read().strip()

        logger.debug("LocalControl: Command returned {}".format(self.exit_code))
        if stdout != '':
            for l in stdout.split('\n'):
                logger.debug("LocalControl: stdout: {}".format(l))
        if stderr != '':
            for l in stderr.split('\n'):
                logger.debug("LocalControl: stderr: {}".format(l))

        return self.exit_code, stdout, stderr

    def getLastExitCode(self):
        return self.exit_code


class SSHControl(Control):

    SSH_TIMEOUT = 15

    def __init__(self, address, port, bench_parser):
        # let's search extra argument we might need
        target_section = bench_parser.config[bench_parser.TARGET_IDENTIFIER]

        keys = {
            "username": 'root',
            "password": None,
            "keyfile": None,
            "system_host_keys": None,
        }

        for key, default in keys.items():

            val = default
            if key in target_section:
                val = target_section[key]

            setattr(self, key, val)

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
        username, password, keyfile = self.strip_variables(
            self.username, self.password, self.keyfile)
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


    def strip_variables(self, *args):
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


    def execute(self, command):
        """Execute a command on a machine, using SSH"""
        self.exit_code = None
        logger.debug("SSHControl: Executing: {}".format(command))
        _, stdout, stderr = self.ssh_client.exec_command(command)
        self.exit_code = stdout.channel.recv_exit_status()
        logger.debug("SSHControl: Command returned {}".format(self.exit_code))
        stdout = stdout.read().decode().strip()
        stderr = stderr.read().decode().strip()
        if stdout != '':
            for l in stdout.split('\n'):
                logger.debug("SSHControl: stdout: {}".format(l.strip()))
        if stderr != '':
            for l in stderr.split('\n'):
                logger.debug("SSHControl: stderr: {}".format(l.strip()))

        return self.exit_code, stdout, stderr

    def getLastExitCode(self):
        return self.exit_code


class TelnetControl(Control):

    TELNET_TIMEOUT = 15

    def __init__(self, address, port, bench_parser):
        target_section = bench_parser.config[bench_parser.TARGET_IDENTIFIER]

        keys = {
            "username": None,
            "password": None,
            "prompt": None,
        }

        for key, default in keys.items():

            val = default
            if key in target_section:
                val = target_section[key]

            setattr(self, key, val)

        self.address = address
        self.port = port
        self.telnet_client = telnetlib.Telnet(address)
        self.prompt = self.prompt.replace('"', '')
        self.is_connected = False


    def isConnected(self):
        return self.is_connected


    def connect(self):
        username, password = self.strip_variables(
                    self.username, self.password)
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

    def strip_variables(self, *args):
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

    def execute(self, command):
        """Execute a command on a machine, using Telnet"""
        self.exit_code = None
        """
        Confirm the command was correctly echoed back and then ask for
        its return code
        """
        logger.debug("TelnetControl: Executing: {}".format(command))
        self.telnet_client.write((command + "\r\n").encode())
        resp = self.telnet_client.read_until((command + "\r\n").encode())
        while True:
            resp = self.telnet_client.read_until(self.prompt.encode())
            if resp is not None:
                break

        stdout = resp.decode()
        stderr = ""
        self.telnet_client.write("echo $?\r\n".encode())
        _, match, before = self.telnet_client.expect([re.compile(b'(\d+)')],
                                                     TelnetControl.TELNET_TIMEOUT)
        self.exit_code = int(match.group(1).decode())
        logger.debug("TelnetControl: Command returned {}".format(self.exit_code))

        if self.exit_code != 0:
            stderr = resp.decode()
        for l in stdout.split('\n'):
            logger.debug("TelnetControl: stdout: {}".format(l.strip()))
        for l in stderr.split('\n'):
            logger.debug("TelnetControl: stderr: {}".format(l.strip()))

        return self.exit_code, stdout, stderr

    def getLastExitCode(self):
        return self.exit_code
