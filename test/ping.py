
import unittest

class TestPing(unittest.TestCase):


    def setUp(self):
        links = self.env.links

        for i, l in enumerate(links, start=1):
            host_addr = "192.168.10.{}/24".format(str(i * 2))
            sut_addr = "192.168.10.{}/24".format(str(i * 2 + 1))

            l.host.addAddress(host_addr)
            l.sut.addAddress(sut_addr)


    def tearDown(self):
        links = self.env.links

        for i, l in enumerate(links, start=1):
            host_addr = "192.168.10.{}/24".format(str(i * 2))
            sut_addr = "192.168.10.{}/24".format(str(i * 2 + 1))

            l.host.delAddress(host_addr)
            l.sut.delAddress(sut_addr)


    def test_ping(self):
        links = self.env.links
        if len(links) == 0:
            self.skipTest("Empty link list")

        for i, _ in enumerate(links, start=1):
            addr = "192.168.10.{}".format(str(i * 2 + 1))
            ping = "ping -c 1 -w 10 " + addr
            print(ping)
            self.env.host.exec(ping)
            self.assertEqual(self.env.host.getLastExitCode(), 0, "Failed to ping System Under Test")

