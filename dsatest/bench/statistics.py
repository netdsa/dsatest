
import logging

logger = logging.getLogger('dsatest')

class Statistics:

    STATS = [
        "rx_broadcast",
        "rx_multicast",
        "rx_octets",
        "rx_packets",
        "rx_unicast",
        "tx_broadcast",
        "tx_multicast",
        "tx_octets",
        "tx_packets",
        "tx_unicast"]


    def __init__(self, interface):
        self.interface = interface
        switch = interface.switch
        self.stats = None

    def __getattr__(self, name):
        if name in Statistics.STATS:
            switch = self.interface.switch
            raw_key = switch.getStatName(name)
            return self.getRaw(raw_key)
        else:
            raise AttributeError(name)

    def getRaw(self, raw_key):
        return self.stats[raw_key]

    def snapshot(self):
        machine = self.interface.machine
        command = "ethtool -S {}".format(self.interface.name)
        exit_code, stdout, stderr = machine.execute(command)
        if exit_code != 0:
            logger.warn("Statistics: failed to get statistics")
            return

        self.stats = dict()

        lines = stdout.split('\n')
        for l in lines[1:]: #skip the "NIC statistics" line
            words = l.split(':')
            if len(words) != 2:
                logger.warn("Stats: Unexpected line while parsing statistics: {}".format(l))
                continue

            key, val = [w.strip() for w in words]
            self.stats[key] = val
