from lets.module import Module
from lets.utility import Utility
import os, sys, unittest


class Http(Module):
    """
    Serve the lets framework as an HTTP REST API
    """
    interactive = True
    platforms = ["linux"]

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant
        to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Enable convert before encode
        parser.add_argument("-p", "--port",
            help="port on which to listen (default=%(default)d)",
            type=int,
            default=80)
        parser.add_argument("-i", "--interface",
            help="interface on which to listen (default=%(default)s)",
            type=str,
            default="0.0.0.0")

        return parser

    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution,
            in bytes
        """
        super().do(data, options)

        # Launch django api from commandline
        os.system(" ".join([
            os.path.join(Utility.core_directory(), "api", "manage.py"),
            "runserver",
            "%(interface)s:%(port)d" % self.options,
            ]))

    @unittest.skip("Interactive")
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
