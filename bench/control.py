
import sys
import logging
import subprocess

import paramiko

logger = logging.getLogger('dsatest')


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


class LocalControl(Control):

    def __init__(self, hostname, bench_parser):
        pass

    def exec(self, command):
        logger.debug("LocalControl: Executing: {}".format(command))
        ret = subprocess.run(command, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.exit_code = ret.returncode
        logger.debug("LocalControl: Command returned {}".format(self.exit_code))
        stdout = ret.stdout.decode(sys.stdout.encoding).strip()
        stderr = ret.stderr.decode(sys.stderr.encoding).strip()
        if stdout != '':
            for l in stdout.split('\n'):
                logger.debug("LocalControl: stdout: {}".format(l))
        if stderr != '':
            for l in stderr.split('\n'):
                logger.debug("LocalControl: stderr: {}".format(l))

    def getLastExitCode(self):
        return self.exit_code


class SSHControl(Control):

    SSH_TIMEOUT = 15

    def __init__(self, address, bench_parser):
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
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.load_system_host_keys(self.system_host_keys)

    def connect(self):
        username, password, keyfile = self.strip_variables(
                self.username, self.password, self.keyfile)
        if password is not None and keyfile is not None:
            self.ssh_client.connect(self.address, username=username,
                                    key_filename=keyfile, password=password,
                                    timeout=SSHControl.SSH_TIMEOUT)
        elif keyfile is not None:
            self.ssh_client.connect(self.address, username=username,
                                    key_filename=keyfile,
                                    timeout=SSHControl.SSH_TIMEOUT)
        elif password is not None:
            self.ssh_client.connect(self.address, username=username,
                                    password=password, look_for_keys=False,
                                    timeout=SSHControl.SSH_TIMEOUT)
        else:
            # let's try with SSH agent, hopefully key will be not encrypted
            self.ssh_client.connect(self.address, username=username,
                                    timeout=SSHControl.SSH_TIMEOUT)

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
        """Execute a command on a machine, using SSH"""
        self.exit_code = None
        logger.debug("SSHControl: Executing: {}".format(command))
        _, stdout, stderr = self.ssh_client.exec_command(command)
        self.exit_code = stdout.channel.recv_exit_status()
        logger.debug("SSHControl: Command returned {}".format(self.exit_code))
        for l in stdout.readlines():
            logger.debug("SSHControl: stdout: {}".format(l.strip()))
        for l in stderr.readlines():
            logger.debug("SSHControl: stderr: {}".format(l.strip()))

    def getLastExitCode(self):
        return self.exit_code

