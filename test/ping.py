
import unittest

class TestPing(unittest.TestCase):

    def test_ping(self):
        links = self.env.get_links()
        if len(links) == 0:
            self.skipTest("Empty link list")

        for l in links:
            host_if = self.env.get_link_interface(l, "host")
            mach_if = self.env.get_link_interface(l, "machine")

            self.env.host.addAddress(host_if, "192.168.10.1/24")
            self.env.sut.addAddress(mach_if, "192.168.10.2/24")

            ping = "ping -c 1 -w 10 192.168.10.2"
            self.env.host.exec(ping)
            self.assertEqual(self.env.host.getLastExitCode(), 0, "Failed to ping System Under Test")

            self.env.host.delAddress(host_if, "192.168.10.1/24")
            self.env.sut.delAddress(mach_if, "192.168.10.2/24")
