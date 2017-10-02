
from squidsa.parser import BenchParser, TargetParser
from .control import LocalControl, SSHControl
from .interface import Interface
from .link import Link
from .machine import Machine

class Bench:

    def __init__(self):
        self.is_setup = False

    def setup(self, bench_config_file):
        env = BenchParser(bench_config_file)
        target_parser = TargetParser(env.target_name)
        host_ctrl = LocalControl()
        username = getattr(env, "ssh_username", None)
        password = getattr(env, "ssh_password", None)
        keyfile = getattr(env, "ssh_keyfile", None)
        sut_ctrl = SSHControl(env.ssh, username=username,
                              password=password, keyfile=keyfile)

        # Create machines involved in the test bench
        # Bridging is a an operation that should only be done on the SUT. To
        # prevent errors, let's add a protection to take care of that.
        self.sut = Machine("SUT", sut_ctrl)
        self.host = Machine("Host", host_ctrl)

        self.links = list()
        self.incomplete_links = list()
        for link_name, link in env.links.items():
            if link.is_incomplete():
                self.incomplete_links.append(link_name)
                continue

            switch, port = target_parser.get_interface_info(link_name)

            host_if = Interface(link.host, self.host)
            sut_if = Interface(link.sut, self.sut, switch, port)

            self.host.addInterface(host_if)
            self.sut.addInterface(sut_if)

            l = Link(link_name, host_if, sut_if)
            self.links.append(l)

            self.is_setup = True


    def connect(self, dry_run=False):
        if not dry_run:
            self.sut.control.connect()

    def disconnect(self, dry_run=False):
        if not dry_run:
            self.sut.control.disconnect()

