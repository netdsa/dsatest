
import configparser

import paramiko

from squidsa.helper.resources import Resource
from .board import BoardParser

class LinkParser:
    """
    Class representing a connection between two machines
    """

    def __init__(self):
        self.host = None
        self.sut = None

    def set_interface_name(self, side, if_name):
        if not side in self.names.keys():
            raise ValueError("Invalid side")
        self.names[side] = if_name

    def is_incomplete(self):
        return self.host is None or self.sut is None

    def __repr__(self):
        return "<Link host: '{0}', machine '{1}'>".format(
                self.host, self.sut)


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
            link.host = val

        for key, val in self.config["machine"].items():
            if not key.startswith(self.LINK_IDENTIFIER):
                continue
            link = self.get_link(key)
            link.sut = val


    def get_link(self, link_name):
        if not link_name in self.links.keys():
            self.links[link_name] = LinkParser()
        return self.links[link_name]

