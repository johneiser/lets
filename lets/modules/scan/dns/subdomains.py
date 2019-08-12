from lets.module import Module
from lets.extensions.docker import DockerExtension


class Subdomains(DockerExtension, Module):
    """
    Attempt to enumerate subdomains of a domain by brute force.
    """
    interactive = True

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Specify target
        parser.add_argument("domain",
            help="domain to query",
            type=str)

        # Allow use of custom wordlist
        parser.add_argument("-l", "--list",
            help="use a custom list of subdomains",
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
            assert self.options.get("domain"), "DOMAIN required"
        except AssertionError as e:
            self.throw(e)

        self.options["wordlist"] = "/usr/share/seclists/Discovery/DNS/subdomains-top1mil-110000.txt"

        # Handle custom wordlist
        io = {}
        wordlist = self.options.get("list")
        if wordlist:
            io[wordlist] = {
                "bind" : self.options.get("wordlist"),
                "mode" : "ro",
            }

        # Build command
        cmd = "gobuster dns -qi -w %(wordlist)s -d %(domain)s" % self.options

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

