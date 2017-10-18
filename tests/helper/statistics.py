
from dsatest.bench.statistics import Statistics

class StatsMonitor:

    def __init__(self, interfaces):
        self.interfaces = interfaces
        self.snapshots = list()

    def snapshot(self):
        stats = dict()
        for i in self.interfaces:
            stats[i] = i.stats.snapshot()

        self.snapshots.append(stats)

        # limit to 2 entries in the list
        while len(self.snapshots) >= 2:
            self.snapshots.pop(0)


    def __getattr__(self, attr):
        if attr not in Statistics.STATS:
            raise AttributeError(name)

        if len(self.snapshots) != 2:
            return ValueError("Unexpected number of snapshots")

        # snapshots is a list of dictionary:
        #   - key: an interface
        #   - val: an instance of Statistics
        # We don't care about the interface for now, so just get a list of all
        # Statistics instances. We do that for the two snapshots in the list.
        stats_before, stats_after = [ s.values() for s in self.snapshots ]

        # On these statistics, we only care about one attribute. Use sum to "coarsely"
        # get the value of this attribute. It's coarse because overflow detection is
        # not (yet?) supported.
        total_before = sum([getattr(s, attr) for s in stats_before])
        total_after  = sum([getattr(s, attr) for s in stats_after])

        return total_after - total_before


    def __enter__(self):
        self.snapshot()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.snapshot()
        return False
