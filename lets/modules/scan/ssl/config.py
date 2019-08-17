from lets.module import Module
from lets.extensions.docker import DockerExtension


class Config(DockerExtension, Module):
    """
    Scan an SSL/TLS endpoint to determine its configuration.
    """

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Specify target
        parser.add_argument("target",
            help="ssl/tls server",
            type=str)

        return parser

    @DockerExtension.ImageDecorator(["local/kali/sslscan:latest"])
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
        try:
            assert self.options.get("target"), "TARGET required"
        except AssertionError as e:
            self.throw(e)

        # Build command
        cmd = "sslscan %(target)s" % self.options

        # Prepare container with input file and output file
        # mounted as volumes
        with self.Container(
            image="local/kali/sslscan:latest",
            command=cmd) as container:

            # Handle container stdout and stderr
            for line in container.logs(stdout=True, stderr=True):
                yield line

            container.wait()

    @DockerExtension.ImageDecorator(["local/kali/sslscan:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
