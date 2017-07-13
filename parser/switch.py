
from squidsa.helper.resources import Resource

class SwitchParser:

    def __init__(self, switch_name):
        self.name = switch_name

        switch_cfg = Resource(Resource.SWITCH, switch_name).get_path()
        self.config = switch_cfg
