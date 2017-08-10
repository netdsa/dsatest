
import configparser
import re
from collections import defaultdict

from squidsa.helper.resources import Resource

from .switch import SwitchParser

class InterfaceInfo:
    """
    Represents an interface (a physical connector) on a board. Each interface
    has an abstract name ("linkXXX"), and holds information about the switch it
    belongs to.
    """

    def __init__(self, name, port, switch=None):
        self.name = name
        self.switch = switch
        self.port = port


    def __repr__(self):
        return "<InterfaceInfo {0} is switch {1}.{2}".format(
                self.name, self.switch.name, self.port)


class BoardParser:
    """
    This class holds information about a board: what are the switches, and which
    ports are connected to physical connectors.

    Config file (in conf/board):
    ------------
    [switch0]
    name = "wag200g"
    port1 = "link0"

    That means the port1 of the wag200g chip is the first port a cable can be
    connected to. This mapping is used to make error reporting easier.
    """

    GROUP_ALL          = 1
    GROUP_BY_SWITCH    = 2


    def __init__(self, board_name):
        self.interfaces = list()
        self.config = configparser.ConfigParser()
        self.board_name = None

        board_cfg = Resource(Resource.BOARD, board_name).get_path()
        path_parsed = self.config.read(board_cfg)
        if (len(path_parsed) != 1):
            error = "Invalid board configuration file: {0}".format(board_cfg)
            raise ValueError(error)

        section_re = re.compile("^switch([\d])+$")
        for s in self.config.sections():
            m = section_re.match(s)
            if m:
                self.parse_switch(s, m.group(1))

        self.__check_unique_interface_name()


    def parse_switch(self, section, switch_id):
        """
        Parse a switch section in the config file and create an object out of it
        """
        interfaces = list()
        switch_name = None
        for key, val in self.config[section].items():
            if key == "name":
                switch_name = val
            elif key.startswith("port"):
                # Pay attention, (val, key) must be inverted here
                interfaces.append(InterfaceInfo(val, key))

        if switch_name is None or len(interfaces) == 0:
            raise ValueError("Missing switch name or port information")

        s = SwitchParser(switch_name)
        for i in interfaces:
            i.switch = s
        self.interfaces.extend(interfaces)


    def get_interface_info(self, if_name):
        for i in self.interfaces:
            if i.name == if_name:
                return (i.switch, i.port)
        raise ValueError("{} is not a know interface".format(if_name))


    def get_interface_infos(self, group=GROUP_ALL):
        if group == BoardParser.GROUP_ALL:
            return self.interfaces
        elif group == BoardParser.GROUP_BY_SWITCH:
            ifs = defaultdict(list)
            for i in self.interfaces:
                ifs[i.switch].append(i)
            return ifs
        else:
            raise ValueError("Invalid group parameter")


    def __check_unique_interface_name(self):
        """
        Make sure an interface name (linkXX) appears only once in the configuration file
        """
        ifs = [i.name for i in self.get_interface_infos(BoardParser.GROUP_ALL)]
        if len(ifs) > len(set(ifs)):
            raise ValueError("Found duplicate interface names")

if __name__ == "__main__":
    b = BoardParser("board-example")

    assert len(b.get_interface_infos(BoardParser.GROUP_ALL)) == 3
    assert len(b.get_interface_infos(BoardParser.GROUP_BY_SWITCH).keys()) == 2
    assert b.get_interface_infos() == b.get_interface_infos(BoardParser.GROUP_ALL)
    try:
        b.get_interface_infos("foobar")
        assert False, "Should not reach this point"
    except ValueError as exception:
        pass
    print("No assert triggered, everything went as expected")
