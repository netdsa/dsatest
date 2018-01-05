
import unittest

from dsatest.bench import bench
from dsatest.tests.helpers import up_and_wait

@unittest.skipIf(not bench.links, "test requires at least 1 link")
class TestBridge(unittest.TestCase):

    def setUp(self):
        self.bridge = bench.target.add_bridge("br0")
        self.bridge.up()

        self.bridge.add_address("192.168.10.1/24")
        for link in bench.links:
            link.host_if.flush_addresses()
            self.bridge.add_interface(link.target_if)
            up_and_wait(link)


    def tearDown(self):
        for link in bench.links:
            self.bridge.del_interface(link.target_if)
            link.host_if.down()
            link.target_if.down()
        self.bridge.down()
        bench.target.del_bridge(self.bridge)


    def test_bridge_ping_one(self):
        for i, link in enumerate(bench.links, start=2):
            host_addr = "192.168.10.{}/24".format(str(i))
            link.host_if.add_address(host_addr)

            """
            No deadline, since we need the bridge to learn our MAC address first
            """
            link.host_if.ping("192.168.10.1", count=1)
            link.host_if.flush_addresses()
