
from .bridge import Bridge

class Machine:
    """Machine being part of the benchtest"""

    def __init__(self, name, control):
        self.interfaces = list()
        self.bridges = list()
        self.name = name
        self.control = control

    def __repr__(self):
        return "<Machine \"{.name}\">".format(self)

    def add_interface(self, interface):
        self.interfaces.append(interface)

    ##################################################
    #           Wrap control functions               #
    ##################################################

    def execute(self, param):
        return self.control.execute(param)


    ##################################################
    # Network related functions, to be used in tests #
    ##################################################

    def up(self, interface):
        command = "ip link set {0} up".format(interface)
        self.control.exec_and_check(command)

    def down(self, interface):
        command = "ip link set {0} down".format(interface)
        self.control.exec_and_check(command)

    def add_address(self, interface, address):
        command = "ip addr add {0} dev {1}".format(address, interface)
        self.control.exec_and_check(command)

    def del_address(self, interface, address):
        command = "ip addr del {0} dev {1}".format(address, interface)
        self.control.exec_and_check(command)

    def flush_addresses(self, interface):
        command = "ip addr flush dev {0}".format(interface)
        self.control.exec_and_check(command)

    def add_bridge(self, bridge_name):
        bridge = Bridge(bridge_name, self)
        bridge.create()
        self.bridges.append(bridge)

        return bridge

    def del_bridge(self, bridge):
        self.bridges.remove(bridge)
        bridge.destroy()

    def ping(self, destination, count=None, deadline=None, from_if=None):
        cmd = "ping "
        if count is not None:
            cmd += " -c {} ".format(count)
        if deadline is not None:
            cmd += " -w {} ".format(deadline)
        if from_if is not None:
            cmd += " -I {} ".format(from_if)
        cmd += " {}".format(destination)
        self.control.exec_and_check(cmd)

    def arp_get(self, address, interface):
        cmd = "cat /proc/net/arp"
        _, stdout, _ = self.control.execute(cmd)
        for line in stdout.splitlines():
            words = line.split()
            if len(words) > 5 and words[0] == address and words[1] == '0x1' and words[5] == interface:
                mac = words[3]
                return mac

        return None
