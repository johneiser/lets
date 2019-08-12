from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import string


class Rundll32(DockerExtension, Module):
    """
    Format a powershell script into an obfuscated cmd.exe command
    by passing the command content through rundll32.exe.
    """
    FLAGS = [
        "None",
        "NoExit",
        "NonInteractive",
        "NoLogo",
        "NoProfile",
        "Command",
        "WindowStyle",
        "ExecutionPolicy",
        "Wow64",
    ]

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant
        to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Specify flags
        parser.add_argument("-f",
            help="flag index to pass to powershell executable",
            dest="flag_indicies",
            type=int,
            choices=range(1,len(self.FLAGS)),
            action="append",
            default=[])
        parser.add_argument("--flag",
            dest="flag_names",
            help="flag name to pass to powershell executable",
            type=str,
            choices=self.FLAGS[1:],
            action="append",
            default=[])

        return parser

    @DockerExtension.ImageDecorator(["local/tools/invoke-obfuscation:latest"])
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

        # Validate input
        try:
            assert data, "Expecting data"
        except AssertionError as e:
            self.throw(e)

        # Build command
        flags = "".join(["%d" % f for f in self.options.get("flag_indicies")])
        flags += "".join(["%d" % self.FLAGS.index(f) for f in self.options.get("flag_names")])
        cmd = "Invoke-Obfuscation -Quiet -ScriptPath /data/in -Command 'LAUNCHER,RUNDLL,%s' | Out-File /data/out" % (flags if flags else "0")
        
        # Prepare input and output files
        with self.IO(data,
            infile="/data/in", outfile="/data/out") as io:

            # Prepare container with input file and output file
            # mounted as volumes
            with self.Container(
                image="local/tools/invoke-obfuscation:latest",
                network_disabled=True,
                volumes=io.volumes,
                entrypoint=["pwsh", "-c"],
                command=[cmd]) as container:

                # Handle container stdout and stderr
                for line in container.logs(
                    stdout=True, stderr=True):
                    self.info(line.strip().decode(), decorate=False)

                # Handle data written to output file
                container.wait()
                yield io.outfile.read()

    @DockerExtension.ImageDecorator(["local/tools/invoke-obfuscation:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test encoding
        test = string.ascii_letters + string.digits
        testcmd = "Write-Output '%s'" % test
        encoded = b"".join(self.do(testcmd.encode(), {"flag_names" : [f for f in self.FLAGS[1:]]}))
        self.assertTrue(len(encoded) > 0, "Printable characters with flag names produced inaccurate results")

        encoded = b"".join(self.do(testcmd.encode(), {"flag_indicies" : range(1,len(self.FLAGS))}))
        self.assertTrue(len(encoded) > 0, "Printable characters with flag indicies produced inaccurate results")
