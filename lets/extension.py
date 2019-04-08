from lets.logger import Logger

class Extension(Logger, object):
    """
    Abstract mixin class to be inherited by each extension,
    enabling the extension of modules with additional functionality.
    """