import os, sys

# Environment variables
TEMP_DIRECTORY = os.path.abspath(os.environ.get("LETS_WORKDIR",
    os.path.sep.join([os.path.abspath(os.path.dirname(__file__)), "data"])))
if not os.path.exists(TEMP_DIRECTORY):
    os.mkdir(TEMP_DIRECTORY)

DEBUG = os.environ.get("LETS_DEBUG") is not None

sys.dont_write_bytecode = os.environ.get("LETS_NOCACHE") is not None

class Utility(object):
    """Class providing generic global utility functions."""

    @staticmethod
    def core_directory() -> str:
        """
        Get the absolute path of the core directory, no matter where
        the file is executed from.

        :return: Absolute path of core directory
        """
        return os.path.abspath(os.path.dirname(__file__))
