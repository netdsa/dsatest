
from dsatest.helper.resources import Resource

class SwitchParser:

    def __init__(self, switch_name, model):
        self.name = switch_name

        switch_cfg = Resource(Resource.SWITCH, model).get_path()
        self.config = switch_cfg
