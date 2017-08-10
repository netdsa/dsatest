
import configparser

import paramiko

from squidsa.helper.resources import Resource
from squidsa.control import SutControl, HostControl
from .board import BoardParser

class Link:
    """
    Class representing a connection between two machines
    """

    SIDE_HOST       = 1
    SIDE_MACHINE    = 2

    def __init__(self):
        self.names = dict({
            Link.SIDE_HOST: None,
            Link.SIDE_MACHINE: None,
            })

    def set_interface_name(self, side, if_name):
        if not side in self.names.keys():
            raise ValueError("Invalid side")
        self.names[side] = if_name

    def is_incomplete(self):
        return None in self.names.values()

    def __repr__(self):
        return "<Link host: '{0}', machine '{1}'>".format(
                self.names[Link.SIDE_HOST],
                self.names[Link.SIDE_MACHINE])


class EnvironmentParser:

    LINK_IDENTIFIER = "link"

    def __init__(self, env_name):
        self.config = configparser.ConfigParser()
        self.links = dict()

        env_cfg = Resource(Resource.ENVIRONMENT, env_name).get_path()
        path_parsed = self.config.read(env_cfg)
        if (len(path_parsed) != 1):
            error = "Invalid environment configuration file: {0}".format(env_cfg)
            raise ValueError(error)

        # TODO: improve parsing to make it more robust
        sections = self.config.sections()
        if not "host" in sections or not "machine" in sections:
            raise ValueError("Missing sections")

        self.board_name = self.config["machine"]["board"]
        self.ssh = self.config["machine"]["ssh"]
        if "ssh_password" in self.config["machine"]:
            self.ssh_password = self.config["machine"]["ssh_password"]
        if "ssh_keyfile" in self.config["machine"]:
            self.ssh_keyfile = self.config["machine"]["ssh_keyfile"]
        if "ssh_username" in self.config["machine"]:
            self.ssh_username = self.config["machine"]["ssh_username"]

        self.create_links()


    def create_links(self):
        for key, val in self.config["host"].items():
            if not key.startswith(self.LINK_IDENTIFIER):
                continue
            link = self.get_link(key)
            link.set_interface_name(Link.SIDE_HOST, val)

        for key, val in self.config["machine"].items():
            if not key.startswith(self.LINK_IDENTIFIER):
                continue
            link = self.get_link(key)
            link.set_interface_name(Link.SIDE_MACHINE, val)


    def get_link(self, link_name):
        if not link_name in self.links.keys():
            self.links[link_name] = Link()
        return self.links[link_name]

class Environment:
    """
    Class holding information about the environment used for tests
    """

    def __init__(self, env_name):
        self.env = EnvironmentParser(env_name)
        self.board = BoardParser(self.env.board_name)
        self.host = HostControl()
        username = getattr(self.env, "ssh_username", None)
        password = getattr(self.env, "ssh_password", None)
        keyfile = getattr(self.env, "ssh_keyfile", None)
        self.sut = SutControl(self.env.ssh, username=username,
                              password=password, keyfile=keyfile)

    def connect(self):
        self.sut.connect()

    def disconnect(self):
        self.sut.disconnect()


    def trim_incomplete_links(self):
        """
        Remove links from the environment that are not connected to both ends.

        This function returns the list of links that were not connected to both
        ends, and remove them from its internal list so that next call to
        `get_links` won't return them anymore.
        """
        incomplete_links = list()
        for link_name, link in self.env.links.items():
            if link.is_incomplete():
                incomplete_links.append(link_name)

        self.links = {link_name: link for link_name, link in self.env.links.items() if
                        link.is_incomplete() is False}
        return incomplete_links


    def get_links(self):
        return self.links.keys()


    def get_link_interface(self, link_name, side):
        if side == "host":
            key = Link.SIDE_HOST
        elif side == "machine":
            key = Link.SIDE_MACHINE
        else:
            raise ValueError("Invalid side value")
        return self.links[link_name].names[key]


    def get_interface_info(self, link_name, side="machine"):
        if side == "host":
            raise NotImplementedError("Getting information for host side not implemented yet")
        elif side != "machine":
            raise ValueError("Unknow side")

        return self.board.get_interface_info(link_name)
