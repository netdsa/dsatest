
import unittest

from dsatest.bench import bench

@unittest.skipIf(not bench.links, "test requires at least 1 link")
class TestBridge(unittest.TestCase):

    def setUp(self):
        self.link = bench.links[0]
        self.link.host_if.flush_addresses()
        self.link.host_if.add_address("192.168.10.2/24")
        self.bridge = bench.target.add_bridge("br0")
        self.bridge.up()


    def tearDown(self):
        self.link.host_if.del_address("192.168.10.2/24")
        self.bridge.down()
        bench.target.del_bridge(self.bridge)


    def test_bridge_ping_one(self):
        self.bridge.add_interface(self.link.target_if)
        self.bridge.add_address("192.168.10.1/24")
        self.link.host_if.ping("192.168.10.1", count=1, deadline=1)
