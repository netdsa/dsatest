
from .bridge import Bridge
from .arp import ArpTable

class Machine:
    """Machine being part of the benchtest"""

    def __init__(self, name, control):
        self.interfaces = list()
        self.bridges = list()
        self.name = name
        self.control = control
        self.arp = ArpTable(self)

    def __repr__(self):
        return "<Machine \"{.name}\">".format(self)

    def addInterface(self, interface):
        self.interfaces.append(interface)

    ##################################################
    #           Wrap control functions               #
    ##################################################

    def exec(self, param):
        return self.control.exec(param)

    def getLastExitCode(self):
        return self.control.getLastExitCode()


    ##################################################
    # Network related functions, to be used in tests #
    ##################################################

    def up(self, interface):
        command = "ip link set {0} up".format(interface)
        self.control.execAndCheck(command)

    def down(self, interface):
        command = "ip link set {0} down".format(interface)
        self.control.execAndCheck(command)

    def addAddress(self, interface, address):
        command = "ip addr add {0} dev {1}".format(address, interface)
        self.control.execAndCheck(command)

    def delAddress(self, interface, address):
        command = "ip addr del {0} dev {1}".format(address, interface)
        self.control.execAndCheck(command)

    def flushAddresses(self, interface):
        command = "ip addr flush dev {0}".format(interface)
        self.control.execAndCheck(command)

    def addBridge(self, bridge_name):
        bridge = Bridge(bridge_name, self)
        bridge.create()
        self.bridges.append(bridge)

        return bridge

    def delBridge(self, bridge):
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
        self.control.execAndCheck(cmd)

