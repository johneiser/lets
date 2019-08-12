from lets.module import Module
from lets.extensions.docker import DockerExtension


class Directories(DockerExtension, Module):
    """
    Attempt to enumerate directories on an HTTP server by brute force.
    """
    interactive = True

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Specify target
        parser.add_argument("target",
            help="http server",
            type=str)

        # Customize HTTP requests
        parser.add_argument("-u", "--useragent",
            help="useragent to use in http requests",
            type=str,
            default="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C)")

        # Allow use of custom wordlist
        parser.add_argument("-l", "--list",
            help="use a custom list of directories",
            type=str,
            default=None)

        return parser

    @DockerExtension.ImageDecorator(["local/kali/gobuster:latest"])
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

        self.options["wordlist"] = "/usr/share/seclists/Discovery/Web-Content/common.txt"

        # Handle custom wordlist
        io = {}
        wordlist = self.options.get("list")
        if wordlist:
            io[wordlist] = {
                "bind" : self.options.get("wordlist"),
                "mode" : "ro",
            }

        # Build command
        cmd = "gobuster dir -qklre -a '%(useragent)s' -w %(wordlist)s -u %(target)s" % self.options

        # Run command in container
        with self.Container(
            image="local/kali/gobuster:latest",
            volumes=io,
            command=cmd) as container:

            container.interact()

    @DockerExtension.ImageDecorator(["local/kali/gobuster:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """

