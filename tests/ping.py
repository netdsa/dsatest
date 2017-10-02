
import unittest

from squidsa.bench import bench

class TestPing(unittest.TestCase):


    def setUp(self):
        links = bench.links

        for i, l in enumerate(links, start=1):
            host_addr = "192.168.10.{}/24".format(str(i * 2))
            target_addr = "192.168.10.{}/24".format(str(i * 2 + 1))

            l.host_if.flushAddresses()
            l.host_if.addAddress(host_addr)
            l.target_if.flushAddresses()
            l.target_if.addAddress(target_addr)


    def tearDown(self):
        links = bench.links

        for i, l in enumerate(links, start=1):
            host_addr = "192.168.10.{}/24".format(str(i * 2))
            target_addr = "192.168.10.{}/24".format(str(i * 2 + 1))

            l.host_if.delAddress(host_addr)
            l.target_if.delAddress(target_addr)


    def test_ping(self):
        links = bench.links
        if len(links) == 0:
            self.skipTest("Empty link list")

        for i, link in enumerate(links, start=1):
            addr = "192.168.10.{}".format(str(i * 2 + 1))
            link.host_if.ping(addr, count=1, deadline=10)

