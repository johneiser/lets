from lets.docker import DockerModule

# Imports required to execute this module
import os, base64, tempfile

class Messagebox(DockerModule):
    """
    Generate Windows x86 shellcode that spawns a message box.
    """
    ICONS = ["NO", "ERROR", "INFORMATION", "WARNING", "QUESTION"]
    EXITFUNCS = ["thread", "process"]

    # A list of docker images required by the module.
    images = [
        "tools/metasploit:latest"
    ]

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Messagebox specific
        parser.add_argument("-t", "--title",
            help="title of window",
            type=str,
            default="MessageBox")
        parser.add_argument("-m", "--message",
            help="message to display",
            type=str,
            default="Hello, from MSF!")
        parser.add_argument("-i", "--icon",
            help="icon to use",
            type=str,
            choices=self.ICONS,
            default="NO")

        # Msfvenom specific
        parser.add_argument("--exitfunc",
            help="exitfunc",
            type=str,
            choices=self.EXITFUNCS,
            default="process")
        parser.add_argument("-b", "--badchars",
            help="characters to avoid",
            type=str)
        parser.add_argument("-e", "--encode",
            help="encoding to avoid characters",
            type=str)

        return parser

    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        DockerModule.do prepares required docker images.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        super().do(data, options)

        # Build core msfvenom command
        cmd = "msfvenom -a x64 --platform windows -p windows/x64/messagebox -f raw -o /data/out"

        # Adjust command with options
        try:
            encode = self.options.get("encode")
            if encode:
                cmd += " -e %(encode)s" % self.options

            badchars = self.options.get("badchars")
            if badchars:
                cmd += " -b %(badchars)s" % self.options

            cmd += " EXITFUNC=%(exitfunc)s TITLE='%(title)s' TEXT='%(message)s' ICON=%(icon)s" % self.options

        except KeyError as e:
            self.throw(e)

        # Prepare output file
        with tempfile.NamedTemporaryFile(dir="/tmp") as outfile:

            # Prepare container with output file mounted as volume
            with self.Container(
                image="tools/metasploit:latest",
                network_disabled=True,
                volumes={
                    outfile.name : {
                        "bind" : "/data/out",
                        "mode" : "rw"
                    }
                },
                command=cmd) as container:

                # Handle container stdout and stderr
                for line in container.logs(stdout=True, stderr=True):
                    self.info(line.strip().decode(), decorate=False)

                # Handle data written to output file
                container.wait()
                yield outfile.read()

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test defaults
        sc = b"".join(self.do(b""))
        self.assertGreater(len(sc),
            0,
            "Defaults produced no results")

        # Test icons
        for icon in self.ICONS:
            self.assertGreater(
                len(b"".join(self.do(b"", {"icon" : icon}))),
                0,
                "Icon (%s) produced no results" % icon)

        # Test exitfuncs
        for exitfunc in self.EXITFUNCS:
            self.assertGreater(len(b"".join(self.do(b"", {"exitfunc" : exitfunc}))),
                0,
                "Exitfunc (%s) produced no results" % exitfunc)
