

class Link:
    """
    Physical link between the Host Machine and the Target Machine (the machine
    being tested). This is just a convenient wrapper to get access to both ends
    of a cable and configure the correspoding interfaces.
    """

    def __init__(self, name, host_if, target_if):
        self.name = name
        self.host_if = host_if
        self.target_if = target_if

    def __repr__(self):
        return "<Link {s.name}: {s.host_if} <-> {s.target_if}>".format(s=self)
