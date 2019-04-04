from lets.docker import DockerModule

# Imports required to execute this module
import os, base64, tempfile

class Messagebox(DockerModule):
    """
    Generate Windows x86 shellcode that spawns a message box.
    """

    # Defaults for configurable options
    options = {
        "title" : "MessageBox",
        "message" : "Hello, from MSF!",
        "icon" : "NO",
        "exitfunc" : "process"
    }

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

        parser.add_argument("-t", "--title",
            help="title of window",
            type=str,
            default=self.options.get("title"))
        parser.add_argument("-m", "--message",
            help="message to display",
            type=str,
            default=self.options.get("message"))
        parser.add_argument("-i", "--icon",
            help="icon to use",
            type=str,
            choices=["NO", "ERROR", "INFORMATION", "WARNING", "QUESTION"],
            default=self.options.get("icon"))

        parser.add_argument("-e", "--exitfunc",
            help="exitfunc",
            type=str,
            choices=["seh", "thread", "process", "none"],
            default=self.options.get("exitfunc"))

        return parser

    def do(self, data:bytes, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        DockerModule.do prepares required docker images.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        super().do(data, options)

        # Prepare output file
        with tempfile.NamedTemporaryFile(dir="/tmp") as outfile:

            # Prepare container with output file mounted as volume
            with self.Container(
                image="tools/metasploit:latest",
                volumes={
                    outfile.name : {
                        "bind" : "/data/out",
                        "mode" : "rw"
                    }
                },
                command="msfvenom -a x64 --platform windows -p windows/x64/messagebox -f raw -o /data/out EXITFUNC=%(exitfunc)s TITLE='%(title)s' TEXT='%(message)s' ICON=%(icon)s" % self.options) as container:

                # Handle container stdout and stderr
                for line in container.logs(stdout=True, stderr=True):
                    self.info(line.strip().decode(), decorate=False)

                # Handle data written to output file
                container.wait()
                yield outfile.read()

        return iter(())

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test generic
        sc = b"".join(self.do(b""))
        self.assertGreater(len(sc), 0)
