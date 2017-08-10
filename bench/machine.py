

class Machine:
    """Machine being part of the benchtest"""

    def __init__(self, name, control):
        self.interfaces = list()
        self.name = name
        self.control = control
        self.allow_bridge_creation = True

    def __repr__(self):
        return "<Machine \"{.name}\">".format(self)

    def setBridgeCreationAllowed(self, val):
        self.allow_bridge_creation = val

    def addInterface(self, interface):
        self.interfaces.append(interface)
