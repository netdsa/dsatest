
from .interface import Interface

class Bridge(Interface):

    def __init__(self, name, machine):
        super(Bridge, self).__init__(name, machine)
        self.interfaces = []

    def create(self):
        command = "ip link add name {} type bridge".format(self.name)
        self.machine.execute(command)

    def destroy(self):
        self.down()
        command = "ip link del {}".format(self.name)
        self.machine.execute(command)

    def add_interface(self, interface):
        self.interfaces.append(interface)
        command = "ip link set {} master {}".format(interface.name, self.name)
        self.machine.execute(command)

    def del_interface(self, interface):
        self.interfaces.remove(interface)
        command = "ip link set {} nomaster".format(interface.name)
        self.machine.execute(command)
