
import unittest

from dsatest.bench import bench

@unittest.skipIf(len(bench.links) == 0, "test requires at least 1 link")
class TestBridge(unittest.TestCase):

    def setUp(self):
        links = bench.links

        for l in enumerate(links):
            l.host_if.flushAddresses()

        self.bridge = bench.target.addBridge("br0")
        self.bridge.up()
        self.bridge.addAddress("192.168.10.1/24")

    def tearDown(self):
        self.bridge.down()
        bench.target.delBridge(self.bridge)


    def test_bridge_ping_all_links(self):
        links = bench.links

        for l in enumerate(links):
            l.host_if.addAddress("192.168.10.2/24")
            self.bridge.addInterface(l.target_if)
            l.host_if.ping("192.168.10.1", count=1, deadline=1)
            l.host_if.delAddress("192.168.10.2/24")
