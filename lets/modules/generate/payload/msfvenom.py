from lets.module import Module
from lets.extensions.docker import DockerExtension

import argparse

class Msfvenom(DockerExtension, Module):
    """
    Generate an `msfvenom`_ payload according to the provided arguments. All
    arguments aside from those specified below will be passed to `msfvenom`_.

    Example: lets generate/payload/msfvenom -a x64 --platform windows -p windows/x64/messagebox

    .. _msfvenom:
        https://www.offensive-security.com/metasploit-unleashed/msfvenom/
    """

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Manually fix usage
        parser.usage = "%(prog)s [-h] [-v] [options] <var=val>"
        parser.epilog = "forbidden arguments: -o, --out (module intercepts output)"

        return parser

    def parse(self, args:list=None) -> dict:
        """
        Parse a list of arguments into a dict of options.

        :param args: List of args to be parsed
        :return: Dict of options
        """
        # Split known and unknown arguments
        known, unknown = self.usage().parse_known_args(args)

        # Add unknown to known["options"]
        options = vars(known)
        options["options"] = unknown

        return options

    @DockerExtension.ImageDecorator(["metasploitframework/metasploit-framework:latest"])
    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        super().do(data, options)

        opts = self.options.get("options")

        # Validate input
        try:
            if opts:
                assert "-o" not in opts, "Unable to specify output (-o)"
                assert "--out" not in opts, "Unable to specify output (--out)"
        except AssertionError as e:
            self.throw(e)

        if data:
            self.warn("Input data detected, ignoring.")

        # Add output, if applicable
        if (opts and 
            "-l" not in opts and 
            "--list" not in opts and 
            "--list-options" not in opts):
            opts.append("-o")
            opts.append("/data/out")

        # Prepare output file
        with self.IO(outfile="/data/out") as io:

            # Prepare container with output file mounted as volume
            with self.Container(
                image="metasploitframework/metasploit-framework:latest",
                network_disabled=True,
                volumes=io.volumes,
                entrypoint="/usr/src/metasploit-framework/msfvenom",
                command=opts) as container:

                # # Handle container stdout and stderr
                for line in container.logs(stdout=True, stderr=True):
                    self.info(line.strip().decode(), decorate=False)

                # Handle data written to output file
                container.wait()
                yield io.outfile.read()

    @DockerExtension.ImageDecorator(["metasploitframework/metasploit-framework:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test sample payload
        sc = b"".join(self.do(None, {"options" : [
            "-p", "windows/meterpreter/reverse_tcp", "LHOST=127.0.0.1"]}))
        self.assertGreater(len(sc),
            0,
            "generic payload produced no results")
