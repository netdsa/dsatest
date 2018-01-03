
import unittest

from dsatest.bench import bench
from dsatest.tests.helpers import up_and_wait

@unittest.skipIf(not bench.links, "Empty link list")
class TestArp(unittest.TestCase):


    def setUp(self):
        for link in bench.links:
            link.host_if.flush_addresses()
            link.target_if.flush_addresses()
            up_and_wait(link)

    def test_port_arp(self):
        links = bench.links

        for i, link in enumerate(links, start=1):
            host_addr = "192.168.{}.1".format(str(10 + i))
            target_addr = "192.168.{}.2".format(str(10 + i))

            link.host_if.add_address("{}/24".format(host_addr))
            link.target_if.add_address("{}/24".format(target_addr))

            link.host_if.ping(target_addr, count=1, deadline=10)
            host_resp = link.host_if.arp_get(target_addr)
            if not host_resp:
                raise ValueError("No ARP entry for {}".format(link.host_if.name))
            target_resp = link.target_if.arp_get(host_addr)
            if not target_resp:
                raise ValueError("No ARP entry for {}".format(link.target_if.name))
            link.host_if.flush_addresses()
            link.target_if.flush_addresses()
