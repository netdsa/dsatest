
import configparser

from dsatest.helper.resources import Resource
from dsatest.bench.statistics import Statistics

class SwitchParser:

    def __init__(self, switch_name, model):
        self.name = switch_name
        self.stats = dict()

        switch_cfg = Resource(Resource.SWITCH, model).get_path()
        self.config = configparser.ConfigParser()

        path_parsed = self.config.read(switch_cfg)
        if (len(path_parsed) != 1):
            error = "Invalid switch configuration file: {0}".format(switch_cfg)
            raise ValueError(error)

        config_stats = self.config["stats"]
        for key in Statistics.STATS:
            self.stats[key] = config_stats[key]


    def getStatName(self, key):
        return self.stats[key]
