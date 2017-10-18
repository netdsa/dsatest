
import logging

logger = logging.getLogger('dsatest')

class Statistics(dict):

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

    def __init__(self, switch_stats_names):
        self.interface = interface
        self.names = switch_stats_names

    def __getattr__(self, name):
        """
        Create additional attribute lookup, by allowing access to members listed in the 'STATS'
        list. That way, a list of predefined statistics are made easily accessible. For other
        statistics that are not core statistics (ie. they are not listed in STATS), the getRaw
        method should be used instead.
        """
        if name in Statistics.STATS:
            raw_key = self.names[key]
            return self.getRaw(raw_key)
        else:
            raise AttributeError(name)

    def getRaw(self, raw_key):
        return super(dict, self)[raw_key]


class StatisticsCapture:

    def __init__(self, interface):
        self.interface = interface

    def snapshot(self):
        machine = self.interface.machine

        command = "ethtool -S {}".format(self.interface.name)
        exit_code, stdout, stderr = machine.execute(command)
        if exit_code != 0:
            logger.warn("Statistics: failed to get statistics")
            return

        # Generate a dictionary with
        #   - key: the name of the statistics as reported by the switch
        #   - val: the name of the statistics as defined by dsatest
        switch = self.interface.switch
        switch_stats_names = {switch.getStatName(stat): stat for stat in Statistics.STATS}

        stats = Statistics(switch_stats_names)

        lines = stdout.split('\n')
        for l in lines[1:]: #skip the "NIC statistics" line
            words = l.split(':')
            if len(words) != 2:
                logger.warn("Stats: Unexpected line while parsing statistics: {}".format(l))
                continue

            key, val = [w.strip() for w in words]
            stats[key] = val

        return stats
