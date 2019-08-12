from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import base64, string, re


class Reorder(DockerExtension, Module):
    """
    Obfuscate a powershell script with string-based manipulation and
    reordering the entire command after concatenating.
    """

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant
        to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

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
        cmd = "Invoke-Obfuscation -Quiet -ScriptPath /data/in -Command 'STRING,2' | Out-File /data/out" % self.options

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
        encoded = b"".join(self.do(testcmd.encode()))
        self.assertTrue(len(encoded) > 0, "Encoding printable characters produced inaccurate results")

        # Skip execution: unstable, too many missing variables in docker container
        return

        # Try to evade errors with missing variables
        compare = encoded.decode().lower()
        while (
            "pshome" in compare or
            "emohsp" in compare or
            "comspec" in compare or
            "cepsmoc" in compare or
            "shellid" in compare or
            "dillehs" in compare or
            "verbosepreference" in compare or
            "ecnereferpesobrev" in compare or
            "mdr" in compare or
            "rdm" in compare
            ):
            encoded = b"".join(self.do(testcmd.encode()))
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
            self.assertEqual(output.decode(), test, "Execution produced inaccurate results")
