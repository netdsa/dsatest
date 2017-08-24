
import unittest

from squidsa.bench import bench

@unittest.skipIf(len(bench.links) == 0, "test requires at least 1 link")
class TestBridge(unittest.TestCase):

    def setUp(self):
        self.link = bench.links[0]
        self.link.host_if.addAddress("192.168.10.2/24")
        self.bridge = bench.sut.addBridge("br0")
        self.bridge.up()


    def tearDown(self):
        self.link.host_if.delAddress("192.168.10.2/24")
        self.bridge.down()
        bench.sut.delBridge(self.bridge)


    def test_add_interface_to_bridge(self):
        self.bridge.addInterface(self.link.sut_if)
        self.bridge.addAddress("192.168.10.1/24")
        self.link.host_if.ping("192.168.10.1", count=1, deadline=1)

