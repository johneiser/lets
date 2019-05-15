from lets.module import Module
from lets.extensions.docker import DockerExtension

import os, unittest

class Smb(DockerExtension, Module):
    """
    Build a listener to serve a local directory as a guest-accessible read-only SMB share.
    """
    interactive = True

    # A list of docker images required by the module.
    images = [
        "dperson/samba:latest"
    ]

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Configure directory to share
        parser.add_argument("directory",
            help="directory to share",
            type=str)

        # Configure interface on which to listen
        parser.add_argument("-i", "--interface",
            help="interface on which to listen",
            type=str,
            required=False,
            default="0.0.0.0")

        return parser

    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        DockerExtension.do prepares required docker images.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        super().do(data, options)

        # Validate input
        directory = self.options.get("directory")
        try:
            assert directory, "Must specify share directory"
            assert os.path.isdir(directory), "Invalid share directory: %s" % directory
        except AssertionError as e:
            self.throw(e)

        # Build command
        path = os.path.abspath(directory)
        name = os.path.basename(path)
        share = "/share"
        cmd = "-s '%s;%s;%s;%s;%s'" % (
            name,  # name
            share, # path
            "yes", # browse
            "yes", # readonly
            "yes"  # guest
            )

        # Prepare container with share directory attached
        with self.Container(
            image="dperson/samba:latest",
            ports={
                "139/tcp" : (self.options.get("interface"), 139),
                "445/tcp" : (self.options.get("interface"), 445)
            },
            volumes={
                path : {
                    "bind" : share,
                    "mode" : "ro"
                }
            },
            command=cmd) as container:

            # Synchronize with container
            container.interact()

    @unittest.skip("Interactive, no tests.")
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
