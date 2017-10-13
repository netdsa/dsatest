
import logging

logger = logging.getLogger('dsatest')

class ArpEntry:

    def __init__(self, ip, hw_type, flags, hw_address, mask, device):
        self.ip = ip
        self.hw_type = hw_type
        self.flags = flags
        self.mac = hw_address
        self.mask = mask
        self.interface = device


class ArpTable:

    def __init__(self, machine):
        self.machine = machine

    def get(self, address=None, interface=None):
        """
        Query ARP table by reading virtual file '/proc/net/arp'. Optionally, an
        address and/or an interface can be passed to this function to filter
        the results. It returns a list of matching entries.
        """
        exit_code, stdout, stderr = self.machine.exec("cat /proc/net/arp")
        entries = list()

        lines = stdout.split('\n')
        for l in lines[1:]:
            words = l.split()
            if len(words) != 6:
                logger.warn("Unexpected line while parsing ARP: {}".format(l))
                continue

            entry = ArpEntry(*words)
            entries.append(entry)

        if address is not None:
            entries = [e for e in entries if e.ip == address]
        if interface is not None:
            entries = [e for e in entries if e.interface == interface]

        return entries
