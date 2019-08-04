from lets.module import Module
from lets.extensions.docker import DockerExtension

import unittest

class Openvas(DockerExtension, Module):
    """
    Launch `OpenVAS`_, the open vulnerability assessment scanner.

    .. _OpenVAS:
        http://www.openvas.org/
    """
    interactive = True

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant
        to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Configure openvas parameters
        parser.add_argument("-u", "--update",
            help="update NVT data",
            action="store_true")
        parser.add_argument("-p", "--password",
            help="admin password",
            type=str,
            required=False,
            default="admin")

        # Configure listen parameters
        parser.add_argument("--interface",
            help="interface on which to listen",
            type=str,
            required=False,
            default="0.0.0.0")
        parser.add_argument("--port",
            help="port on which to listen",
            type=int,
            required=False,
            default=443)

        return parser

    @DockerExtension.ImageDecorator(["atomicorp/openvas:latest"])
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

        # Prepare container
        with self.Container(
            image="atomicorp/openvas:latest",
            ports={
                "443/tcp" : (self.options.get("interface"), self.options.get("port"))
            },
            environment={
                "OV_PASSWORD" : self.options.get("password"),
                "OV_UPDATE" : "yes" if self.options.get("update") else "no"
            }) as container:

            # Enter container
            container.interact()

    @unittest.skip("Interactive, and docker image too big")
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
