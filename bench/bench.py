
from dsatest.parser import BenchParser, TargetParser
from dsatest.helper.scheme import URI
from .control import LocalControl, SSHControl, TelnetControl
from .interface import Interface
from .link import Link
from .machine import Machine

class Bench:

    controls = {
        URI.Scheme.LOCAL:   LocalControl,
        URI.Scheme.SSH:     SSHControl,
        URI.Scheme.TELNET:  TelnetControl,
    }

    def __init__(self):
        self.is_setup = False
        self.dry_run = False
        self.target = None
        self.host = None
        self.links = None
        self.incomplete_links = None

    def setup(self, bench_config_file):
        bench_parser = BenchParser(bench_config_file)
        target_parser = TargetParser(bench_parser.target_name)

        default_scheme = URI.Scheme.LOCAL
        host_scheme = URI(bench_parser.host_control)
        target_scheme = URI(bench_parser.target_control)

        host_ctrl = self.controls[host_scheme.get_scheme(default_scheme)](
            host_scheme.get_host(), host_scheme.get_port(),
            bench_parser)
        target_ctrl = self.controls[target_scheme.get_scheme(default_scheme)](
            target_scheme.get_host(), target_scheme.get_port(),
            bench_parser)

        # Create machines involved in the test bench
        self.target = Machine("Target", target_ctrl)
        self.host = Machine("Host", host_ctrl)

        self.links = list()
        self.incomplete_links = list()
        for link_name, link in bench_parser.links.items():
            if link.is_incomplete():
                self.incomplete_links.append(link_name)
                continue

            switch, port = target_parser.get_interface_info(link_name)

            host_if = Interface(link.host, self.host)
            target_if = Interface(link.target, self.target, switch, port)

            self.host.add_interface(host_if)
            self.target.add_interface(target_if)

            new_link_instance = Link(link_name, host_if, target_if)
            self.links.append(new_link_instance)

            self.is_setup = True


    def set_dry_run(self, dry_run):
        self.dry_run = dry_run

    def connect(self):
        if not self.dry_run:
            self.target.control.connect()

    def disconnect(self, dry_run=False):
        if not self.dry_run:
            self.target.control.disconnect()
