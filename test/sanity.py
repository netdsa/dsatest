
import unittest

from squidsa.bench import Interface

class TestSanity(unittest.TestCase):

    def test_hasattr_env(self):
        self.assertTrue(hasattr(self, "env"))

    def test_links_is_iterable(self):
        self.assertTrue(iter(self.env.links))

    def test_link_has_interfaces(self):
        for link in self.env.links:
            self.assertIsInstance(link.host_if, Interface)
            self.assertIsInstance(link.sut_if, Interface)

    def test_interface_member(self):
        for link in self.env.links:
            interface = link.sut_if
            self.assertIsInstance(interface.name, str)
            self.assertIsInstance(interface.port_id, str)


    def test_link_names(self):
        links = self.env.links
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
        for link in self.env.links:
            ifs = [ link.host_if, link.sut_if ]
            for interface in ifs:
                self.assertTrue(hasattr(interface, "up"))
                self.assertTrue(hasattr(interface, "down"))
                self.assertTrue(hasattr(interface, "addAddress"))
                self.assertTrue(hasattr(interface, "delAddress"))

    def test_machine_api(self):
        machs = [ self.env.host, self.env.sut ]
        for mach in machs:
            self.assertTrue(hasattr(mach, "up"))
            self.assertTrue(hasattr(mach, "down"))
            self.assertTrue(hasattr(mach, "addAddress"))
            self.assertTrue(hasattr(mach, "delAddress"))
            self.assertTrue(hasattr(mach, "ping"))

