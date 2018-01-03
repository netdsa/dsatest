
import unittest

from dsatest.bench import bench

@unittest.skipIf(not bench.links, "Empty link list")
class TestPing(unittest.TestCase):

    def get_address(self, offset, side, prefix_length=None):
        if side == "host":
            side = "1"
        elif side == "target":
            side = "2"
        else:
            raise ValueError("unexpected side")

        address = "192.168.{}.{}".format(str(10 + offset), side)
        if prefix_length:
            address = "{}/{}".format(address, prefix_length)

        return address


    def setUp(self):
        links = bench.links

        for i, link in enumerate(links):
            link.host_if.up()
            link.target_if.up()
            link.host_if.flush_addresses()
            link.host_if.add_address(self.get_address(i, "host", 24))
            link.target_if.flush_addresses()
            link.target_if.add_address(self.get_address(i, "target", 24))


    def tearDown(self):
        links = bench.links

        for i, link in enumerate(links):
            link.host_if.del_address(self.get_address(i, "host", 24))
            link.host_if.down()
            link.target_if.del_address(self.get_address(i, "target", 24))
            link.target_if.down()


    def test_port_ping_all(self):
        for i, link in enumerate(bench.links):
            addr = self.get_address(i, "target")
            link.host_if.ping(addr, count=1, deadline=10)
