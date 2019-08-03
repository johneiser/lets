from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import base64, string


class Encoding(DockerExtension, Module):
    """
    Obfuscate a powershell script with encoding-based manipulation.
    """
    TECHNIQUES = [
        "1",    # Encode entire command as ASCII
        "2",    # Encode entire command as Hex
        "3",    # Encode entire command as Octal
        "4",    # Encode entire command as Binary
        "5",    # Encrypt entire command as SecureString (AES)
        "6",    # Encode entire command as BXOR
        "7",    # Encode entire command as Special Characters
        "8",    # Encode entire command as Whitespace
    ]

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant
        to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Specify technique
        parser.add_argument("-t", "--technique",
            help="technique to use in obfuscation",
            type=str,
            choices=self.TECHNIQUES,
            default="1")

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
            technique = self.options.get("technique")
            assert technique in self.TECHNIQUES, "Invalid technique: %s (%s)" % (technique, str(self.TECHNIQUES))
        except AssertionError as e:
            self.throw(e)

        # Build command
        cmd = "Invoke-Obfuscation -Quiet -ScriptPath /data/in -Command 'ENCODING,%(technique)s' | Out-File /data/out" % self.options

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
        for technique in self.TECHNIQUES:
            test = string.ascii_letters + string.digits
            testcmd = "Write-Output '%s'" % test
            encoded = b"".join(self.do(testcmd.encode(), {"technique" : technique}))
            self.assertTrue(len(encoded) > 0, "Technique %s produced inaccurate results" % technique)

            # Skip execution: unstable, too many missing variables in docker container
            continue

            # Try to evade errors with missing variables
            compare = encoded.decode().lower()
            while (
                "pshome" in compare or
                "comspec" in compare or
                "shellid" in compare or
                "verbosepreference" in compare or
                "mdr" in compare
                ):
                encoded = b"".join(self.do(testcmd.encode(), {"technique" : technique}))
                compare = encoded.decode().lower()

            # Base64 encode to get past the container layer
            cmd = base64.b64encode(encoded.decode().encode("utf-16-le")).decode()

            # Test execution
            with self.Container(
                image="local/tools/invoke-obfuscation:latest",
                network_disabled=True,
                entrypoint=["pwsh", "-e"],
                command=[cmd]) as container:

                # Fetch output
                output = [line.strip() for line in container.logs(stdout=True, stderr=True)][0]

                # Wait for container to cleanup
                container.wait()

                # Verify execution was successful
                self.assertEqual(output.decode(), test, "Execution of technique %s produced inaccurate results" % technique)
