
import unittest

from dsatest.bench import bench

@unittest.skipIf(not bench.links, "Empty link list")
class TestPing(unittest.TestCase):

    def setUp(self):
        links = bench.links

        for i, link in enumerate(links, start=1):
            host_addr = "192.168.10.{}/24".format(str(i * 2))
            target_addr = "192.168.10.{}/24".format(str(i * 2 + 1))

            link.host_if.up()
            link.target_if.up()
            link.host_if.flush_addresses()
            link.host_if.add_address(host_addr)
            link.target_if.flush_addresses()
            link.target_if.add_address(target_addr)


    def tearDown(self):
        links = bench.links

        for i, link in enumerate(links, start=1):
            host_addr = "192.168.10.{}/24".format(str(i * 2))
            target_addr = "192.168.10.{}/24".format(str(i * 2 + 1))

            link.host_if.del_address(host_addr)
            link.host_if.down()
            link.target_if.del_address(target_addr)
            link.target_if.down()


    def test_port_ping_all(self):
        for i, link in enumerate(bench.links, start=1):
            addr = "192.168.10.{}".format(str(i * 2 + 1))
            link.host_if.ping(addr, count=1, deadline=10)
