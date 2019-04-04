import os, sys

class Utility(object):
    """
    Class providing generic global utility functions.
    """

    @staticmethod
    def core_directory() -> str:
        """
        Get the absolute path of the core directory, no matter where
        the file is executed from.

        :return: Absolute path of core directory
        """
        return os.path.dirname(__file__)