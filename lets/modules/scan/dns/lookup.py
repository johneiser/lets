from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module

class Lookup(DockerExtension, Module):
    """
    Perform an address lookup for a domain.
    """

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Specify query parameters
        parser.add_argument("domain",
            help="domain to query",
            type=str)

        # Change query destination
        parser.add_argument("-n", "--nameserver",
            help="nameserver to query against",
            type=str,
            default="8.8.8.8")

        return parser

    @DockerExtension.ImageDecorator(["local/kali/dnsrecon:latest"])
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
            assert self.options.get("domain"), "Domain required"
        except AssertionError as e:
            self.throw(e)

        # Build command
        cmd = "dnsrecon -n %(nameserver)s -d %(domain)s" % self.options

        # Prepare container with input file and output file
        # mounted as volumes
        with self.Container(
            image="local/kali/dnsrecon:latest",
            command=cmd) as container:

            # Handle container stdout and stderr
            for line in container.logs(stdout=True, stderr=True):
                yield line

            container.wait()

    @DockerExtension.ImageDecorator(["local/kali/dnsrecon:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
