from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import os


class Http(DockerExtension, Module):
    """
    Build a listener to serve a local directory over HTTP.
    """
    interactive = True

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Configure directory to serve
        parser.add_argument("directory",
            help="directory to serve",
            type=str)

        # Configure listen parameters
        parser.add_argument("-i", "--interface",
            help="interface on which to listen (default=%(default)s)",
            type=str,
            required=False,
            default="0.0.0.0")
        parser.add_argument("-p", "--port",
            help="port on which to listen (default=%(default)d)",
            type=int,
            required=False,
            default=80)

        return parser

    @DockerExtension.ImageDecorator(["nginx:latest"])
    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        super().do(data, options)

        # Validate input
        directory = self.options.get("directory")
        try:
            assert directory, "Must specify directory to serve"
            assert os.path.isdir(directory), "Invalid directory: %s" % directory
        except AssertionError as e:
            self.throw(e)

        # Prepare directory to attach
        path = os.path.abspath(directory)
        self.info("Mounting directory: %s" % path)

        # Prepare container with directory attached at webroot
        with self.Container(
            image="nginx:latest",
            ports={
                "80/tcp" : (self.options.get("interface"), self.options.get("port", 80)),
            },
            volumes={
                path : {
                    "bind" : "/usr/share/nginx/html",
                    "mode" : "ro"
                }
            }) as container:

            # Synchronize with container
            container.interact()

    @DockerExtension.ImageDecorator(["nginx:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
