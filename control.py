
import re
import subprocess

import paramiko


class Control(object):

    def exec(self):
        raise NotImplementedError()

    def getLastExitCode(self):
        raise NotImplementedError()

    def checkExitCode(self, expected_exit_code):
        actual_exit_code = self.getLastExitCode()
        if actual_exit_code != expected_exit_code:
            raise ValueError("Exit code mismatch. Got {}, expected {}".format(
                actual_exit_code, expected_exit_code))

    def execAndCheck(self, command, expected_exit_code=0):
        self.exec(command)
        self.checkExitCode(expected_exit_code)

    def up(self, interface):
        command = "ip link set {0} up".format(interface)
        self.execAndCheck(command)

    def down(self, interface):
        command = "ip link set {0} down".format(interface)
        self.execAndCheck(command)

    def addAddress(self, interface, address):
        command = "ip addr add {0} dev {1}".format(address, interface)
        self.execAndCheck(command)

    def delAddress(self, interface, address):
        command = "ip addr del {0} dev {1}".format(address, interface)
        self.execAndCheck(command)


class HostControl(Control):

    def exec(self, command):
        ret = subprocess.run(command, shell=True)
        self.exit_code = ret.returncode

    def getLastExitCode(self):
        return self.exit_code


class SutControl(Control):

    SSH_TIMEOUT = 15

    def __init__(self, address, username='root', password=None, keyfile=None):
        self.address = address
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.load_system_host_keys()
        self.username = username
        self.password = password
        self.keyfile = keyfile

    def connect(self):
        username, password, keyfile = self.strip_variables(
                self.username, self.password, self.keyfile)
        if password is not None and keyfile is not None:
            self.ssh_client.connect(self.address, username=username,
                                    key_filename=keyfile, password=password,
                                    timeout=SutControl.SSH_TIMEOUT)
        elif keyfile is not None:
            self.ssh_client.connect(self.address, username=username,
                                    key_filename=keyfile,
                                    timeout=SutControl.SSH_TIMEOUT)
        elif password is not None:
            self.ssh_client.connect(self.address, username=username,
                                    password=password, look_for_keys=False,
                                    timeout=SutControl.SSH_TIMEOUT)
        else:
            # let's try with SSH agent, hopefully key will be not encrypted
            self.ssh_client.connect(self.address, username=username,
                                    timeout=SutControl.SSH_TIMEOUT)

    def disconnect(self):
        self.ssh_client.close()


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


    def exec(self, command):
        """Execute a command on the SUT, using SSH"""
        self.exit_code = None
        command += '; echo exit code $? ; exit\n'
        _, stdout, stderr = self.ssh_client.exec_command(command)
        results = str(stdout.read())
        self.error = stderr.read()

        pattern = re.compile('exit code ([a-z0-9]+)')
        match = pattern.search(results)
        if match:
            self.exit_code = int(match.group(1))
        return results

    def getLastExitCode(self):
        return self.exit_code

