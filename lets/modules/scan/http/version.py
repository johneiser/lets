from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module

class Version(DockerExtension, Module):
    """
    Scan an HTTP server to determine the software versions it uses.
    """

    # A list of docker images required by the module.
    images = [
        "local/kali/whatweb:latest"
    ]

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Specify destination
        parser.add_argument("url",
            help="url of http server",
            type=str)

        # Customize HTTP requests
        parser.add_argument("-u", "--useragent",
            help="useragent to use in http requests",
            type=str,
            default="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C)")

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
        try:
            assert self.options.get("url"), "URL required"
        except AssertionError as e:
            self.throw(e)

        # Build command
        cmd = "whatweb -a3 --user-agent '%(useragent)s' %(url)s" % self.options

        # Prepare container with input file and output file
        # mounted as volumes
        with self.Container(
            image="local/kali/whatweb:latest",
            command=cmd) as container:

            # Handle container stdout and stderr
            for line in container.logs(stdout=True, stderr=True):
                yield line

            container.wait()

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Verify required docker images can be produced
        self._prep()
