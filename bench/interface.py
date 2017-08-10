
class Interface:
    """
    Network interface on a Machine. The name must be a string on which
    commands can be operated (like `ip link`)
    """

    def __init__(self, name, machine, switch=None, port_id=None):
        self.name = name
        self.machine = machine
        self.switch = switch
        self.port_id = port_id


    def __repr__(self):
        if self.switch:
            return "<Interface {s.machine.name} {s.name} {s.switch.name}.{s.port_id}>".format(s=self)
        else:
            return "<Interface {s.machine.name} {s.name}>".format(s=self)

    def up(self):
        self.machine.control.up(self.name)

    def down(self):
        self.machine.control.down(self.name)

    def addAddress(self, address):
        self.machine.control.addAddress(address, self.name)

    def delAddress(self, interface, address):
        self.machine.control.delAddress(address, self.name)
