
import os
import pkg_resources

from dsatest import settings


class Resource:
    """
    This class is a helper to find configuration files within dsatest. Typical
    invocation would look like:

    r = Resource(Resource.TARGET, "wag200g")
    print(r.get_path())

    The benefit of using this helper is that files can be easily located even
    if this application is distributed as a Python Egg.
    """

    SWITCH          = 1
    TARGET          = 2


    def __init__(self, resource_type, name):
        if resource_type == Resource.SWITCH:
            type_ = "switch"
        elif resource_type == Resource.TARGET:
            type_ = "target"
        else:
            raise ValueError("Invalid resource_type")

        if not name.endswith(".cfg"):
            name = '{0}.cfg'.format(name)

        conf_path = settings.get_option(settings.CONF_PATH)
        if conf_path:
            self.cfg = os.path.join(conf_path, type_, name)
            if os.path.exists(self.cfg):
                return

        resource_path = '/'.join(('conf', type_, name))

        resource_package = "dsatest"
        self.cfg = pkg_resources.resource_filename(resource_package, resource_path)
        if not os.path.exists(self.cfg):
            raise ValueError("Cannot find resource {} of type {}".format(name, type_))

    def get_path(self):
        return self.cfg
