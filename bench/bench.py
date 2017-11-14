
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

    def setup(self, bench_config_file):
        bench_parser = BenchParser(bench_config_file)
        target_parser = TargetParser(bench_parser.target_name)

        default_scheme = URI.Scheme.LOCAL
        host_scheme = URI(bench_parser.host_control)
        target_scheme = URI(bench_parser.target_control)

        host_ctrl = self.controls[host_scheme.getScheme(default_scheme)](
                host_scheme.getHost(), host_scheme.getPort(),
                bench_parser)
        target_ctrl = self.controls[target_scheme.getScheme(default_scheme)](
                target_scheme.getHost(), target_scheme.getPort(),
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

            self.host.addInterface(host_if)
            self.target.addInterface(target_if)

            new_link_instance = Link(link_name, host_if, target_if)
            self.links.append(new_link_instance)

            self.is_setup = True


    def connect(self, dry_run=False):
        if not dry_run:
            self.target.control.connect()

    def disconnect(self, dry_run=False):
        if not dry_run:
            self.target.control.disconnect()

