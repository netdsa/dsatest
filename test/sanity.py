
import unittest

from squidsa.bench import Interface, bench

class TestSanity(unittest.TestCase):

    def test_bench_is_not_none(self):
        self.assertTrue(bench is not None)

    def test_bench_setup(self):
        self.assertTrue(bench.is_setup)

    def test_links_is_iterable(self):
        self.assertTrue(iter(bench.links))

    def test_link_has_interfaces(self):
        for link in bench.links:
            self.assertIsInstance(link.host_if, Interface)
            self.assertIsInstance(link.sut_if, Interface)

    def test_interface_member(self):
        for link in bench.links:
            interface = link.sut_if
            self.assertIsInstance(interface.name, str)
            self.assertIsInstance(interface.port_id, str)

    def test_link_names(self):
        links = bench.links
        if len(links) == 0:
            self.skipTest("Empty link list")

        for l in links:
            host = l.host_if.name
            sut = l.sut_if.name
            self.assertIsInstance(host, str)
            self.assertIsInstance(sut, str)
            self.assertTrue(len(host) > 0)
            self.assertTrue(len(sut) > 0)

    def test_interface_api(self):
        for link in bench.links:
            ifs = [ link.host_if, link.sut_if ]
            for interface in ifs:
                self.assertTrue(hasattr(interface, "up"))
                self.assertTrue(hasattr(interface, "down"))
                self.assertTrue(hasattr(interface, "addAddress"))
                self.assertTrue(hasattr(interface, "delAddress"))

    def test_machine_api(self):
        machs = [ bench.host, bench.sut ]
        for mach in machs:
            self.assertTrue(hasattr(mach, "up"))
            self.assertTrue(hasattr(mach, "down"))
            self.assertTrue(hasattr(mach, "addAddress"))
            self.assertTrue(hasattr(mach, "delAddress"))
            self.assertTrue(hasattr(mach, "ping"))

