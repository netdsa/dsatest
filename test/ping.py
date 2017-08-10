
import unittest

class TestPing(unittest.TestCase):


    def setUp(self):
        links = self.env.get_links()

        for i, l in enumerate(links, start=1):
            host_if = self.env.get_link_interface(l, "host")
            mach_if = self.env.get_link_interface(l, "machine")

            host_addr = "192.168.10.{}/24".format(str(i * 2))
            mach_addr = "192.168.10.{}/24".format(str(i * 2 + 1))

            self.env.host.addAddress(host_if, host_addr)
            self.env.sut.addAddress(mach_if, mach_addr)


    def tearDown(self):
        links = self.env.get_links()

        for i, l in enumerate(links, start=1):
            host_if = self.env.get_link_interface(l, "host")
            mach_if = self.env.get_link_interface(l, "machine")

            host_addr = "192.168.10.{}/24".format(str(i * 2))
            mach_addr = "192.168.10.{}/24".format(str(i * 2 + 1))

            self.env.host.delAddress(host_if, host_addr)
            self.env.sut.delAddress(mach_if, mach_addr)


    def test_ping(self):
        links = self.env.get_links()
        if len(links) == 0:
            self.skipTest("Empty link list")

        for i, _ in enumerate(links, start=1):
            addr = "192.168.10.{}".format(str(i * 2 + 1))
            ping = "ping -c 1 -w 10 " + addr
            print(ping)
            self.env.host.exec(ping)
            self.assertEqual(self.env.host.getLastExitCode(), 0, "Failed to ping System Under Test")

