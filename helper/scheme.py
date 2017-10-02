
import re

class URI:

    class Scheme:
        LOCAL           = 1
        SSH             = 2

    to_constants = {
        "ssh":      Scheme.SSH,
        "local":    Scheme.LOCAL,
    }

    def __init__(self, uri):
        self.uri = uri

        if self.uri:
            pattern = re.compile("^([a-z]+)://(.+)$")
            match = pattern.match(self.uri)
            if match:
                self.const = self.to_constants[match.group(1)]
                self.host = match.group(2)

    def getScheme(self, default=None):
        return getattr(self, "const", default)

    def getHost(self, default=None):
        return getattr(self, "host", default)
