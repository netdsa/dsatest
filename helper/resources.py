
import os
import pkg_resources

from squidsa import settings


class Resource:
    """
    This class is a helper to find configuration files within squidsa. Typical
    invocation would look like:

    r = Resource(Resource.BOARD, "wag200g")
    print(r.get_path())

    The benefit of using this helper is that files can be easily located even
    if this application is distributed as a Python Egg.
    """

    SWITCH          = 1
    BOARD           = 2
    ENVIRONMENT     = 3


    def __init__(self, resource_type, name):
        if resource_type == Resource.SWITCH:
            t = "switch"
        elif resource_type == Resource.BOARD:
            t = "board"
        elif resource_type == Resource.ENVIRONMENT:
            t = "env"
        else:
            raise ValueError("Invalid resource_type")

        if not name.endswith(".cfg"):
            name = '{0}.cfg'.format(name)

        if settings.get(settings.CONF_PATH) is not None:
            self.cfg = os.path.join(settings.conf_path, t, name)
        else:
            resource_path = '/'.join(('conf', t, name))

            resource_package = "squidsa"
            self.cfg = pkg_resources.resource_filename(resource_package, resource_path)

    def get_path(self):
        return self.cfg
