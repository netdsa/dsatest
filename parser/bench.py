
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
        return "<Link host: '{0}', sut '{1}'>".format(
                self.host, self.sut)


class BenchParser:

    LINK_IDENTIFIER = "link"
    HOST_IDENTIFIER = "host"
    SUT_IDENTIFIER = "sut"

    def __init__(self, bench_config_file):
        self.config = configparser.ConfigParser()
        self.links = dict()

        path_parsed = self.config.read(bench_config_file)
        if (len(path_parsed) != 1):
            error = "Invalid environment configuration file: {0}".format(bench_config_file)
            raise ValueError(error)

        # TODO: improve parsing to make it more robust
        sections = self.config.sections()
        if (not self.HOST_IDENTIFIER in sections or
                not self.SUT_IDENTIFIER in sections):
            raise ValueError("Missing sections")

        sut_section = self.config[self.SUT_IDENTIFIER]
        self.board_name = sut_section["board"]
        self.ssh = sut_section["ssh"]
        if "ssh_password" in sut_section:
            self.ssh_password = sut_section["ssh_password"]
        if "ssh_keyfile" in sut_section:
            self.ssh_keyfile = sut_section["ssh_keyfile"]
        if "ssh_username" in sut_section:
            self.ssh_username = sut_section["ssh_username"]

        self.create_links()


    def create_links(self):
        host_section = self.config[self.HOST_IDENTIFIER]
        sut_section = self.config[self.SUT_IDENTIFIER]
        for key, val in host_section.items():
            if not key.startswith(self.LINK_IDENTIFIER):
                continue
            link = self.get_link(key)
            link.host = val

        sut_section = self.config[self.SUT_IDENTIFIER]
        for key, val in sut_section.items():
            if not key.startswith(self.LINK_IDENTIFIER):
                continue
            link = self.get_link(key)
            link.sut = val


    def get_link(self, link_name):
        if not link_name in self.links.keys():
            self.links[link_name] = LinkParser()
        return self.links[link_name]

