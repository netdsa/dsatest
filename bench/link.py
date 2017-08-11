

class Link:
    """
    Physical link between the Host Machine and the System Under Test
    (SUT). This just a convenient wrapper to get access to both ends of
    a cable and configure the correspoding interfaces.
    """

    def __init__(self, name, host_if, sut_if):
        self.name = name
        self.host_if = host_if
        self.sut_if = sut_if

    def __repr__(self):
        return "<Link {s.name}: {s.host} <-> {s.sut}>".format(s=self)
