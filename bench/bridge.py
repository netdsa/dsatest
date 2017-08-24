
from .interface import Interface

class Bridge(Interface):

    def __init__(self, name, machine):
        super(Bridge, self).__init__(name, machine)
        self.interfaces = []

    def create(self):
        command = "brctl addbr {}".format(self.name)
        self.machine.exec(command)

    def destroy(self):
        self.down()
        command = "brctl delbr {}".format(self.name)
        self.machine.exec(command)

    def addInterface(self, interface):
        self.interfaces.append(interface)
        command = "brctl addif {} {}".format(self.name, interface.name)
        self.machine.exec(command)

    def delInterface(self, interface):
        self.interfaces.remove(interface)
        command = "brctl delif {} {}".format(self.name, interface.name)
        self.machine.exec(command)
