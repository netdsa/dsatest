
import unittest

from squidsa.parser import SwitchParser

class TestSanity(unittest.TestCase):

    def test_hasattr_env(self):
        self.assertTrue(hasattr(self, "env"))


    def test_links_is_iterable(self):
        self.assertTrue(iter(self.env.get_links()))


    def test_link_names(self):
        links = self.env.get_links()
        if len(links) == 0:
            self.skipTest("Empty link list")

        for l in links:
            host = self.env.get_link_interface(l, "host")
            mach = self.env.get_link_interface(l, "machine")
            self.assertIsInstance(host, str)
            self.assertIsInstance(mach, str)
            self.assertTrue(len(host) > 0)
            self.assertTrue(len(mach) > 0)
            with self.assertRaises(ValueError):
                self.env.get_link_interface(l, None)


    def test_interface_info(self):
        links = self.env.get_links()
        if len(links) == 0:
            self.skipTest("Empty link list")

        for l in links:
            ret = self.env.get_interface_info(l)
            self.assertEquals(len(ret), 2)
            switch, port = ret
            with self.assertRaises(NotImplementedError):
                self.env.get_interface_info(l, "host")
            with self.assertRaises(ValueError):
                self.env.get_interface_info(l, "foobar")

            self.assertIsInstance(switch, SwitchParser)
            self.assertIsInstance(port, str)
