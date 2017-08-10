
import unittest

from squidsa.bench import Interface

class TestSanity(unittest.TestCase):

    def test_hasattr_env(self):
        self.assertTrue(hasattr(self, "env"))

    def test_links_is_iterable(self):
        self.assertTrue(iter(self.env.links))

    def test_link_has_interfaces(self):
        for link in self.env.links:
            self.assertIsInstance(link.host, Interface)
            self.assertIsInstance(link.sut, Interface)

    def test_interface_member(self):
        for link in self.env.links:
            interface = link.sut
            self.assertIsInstance(interface.name, str)
            self.assertIsInstance(interface.port_id, str)


    def test_link_names(self):
        links = self.env.links
        if len(links) == 0:
            self.skipTest("Empty link list")

        for l in links:
            host = l.host.name
            sut = l.sut.name
            self.assertIsInstance(host, str)
            self.assertIsInstance(sut, str)
            self.assertTrue(len(host) > 0)
            self.assertTrue(len(sut) > 0)

