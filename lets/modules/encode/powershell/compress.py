from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import gzip, base64, string


class Compress(DockerExtension, Module):
    """
    Compress and Base64 encode a powershell script and prepend a
    decode/decompress stub.
    """

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        return parser

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
            assert data, "Expecting data"
        except AssertionError as e:
            self.throw(e)

        # Compress command
        compressed = gzip.compress(data, compresslevel=9)

        # Encode command
        encoded = base64.b64encode(compressed)
        self.options["encoded"] = encoded.decode()
        
        # Place encoded command in harness
        cmd = ("IEX "+

            # Read bytes from stream
            "(New-Object System.IO.StreamReader("+

            # Decompress stream
            "$(New-Object System.IO.Compression.GzipStream("+

            # Place bytes in stream
            "$(New-Object System.IO.MemoryStream("+

            # Decode bytes
            # ---------------
            ",[System.Convert]::FromBase64String('%(encoded)s')"+
            # ---------------

            ")"+
            "),[System.IO.Compression.CompressionMode]::Decompress)"+
            "),[System.Text.Encoding]::UTF8)"+
            ").ReadToEnd()") % self.options

        # Convert harness to bytes and return
        yield cmd.encode()

    @DockerExtension.ImageDecorator(["mcr.microsoft.com/powershell:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test encoding (TODO: gzip header not consistent)
        # self.assertTrue(
        #     b"10C/wEAAf/+AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/3OMBSkAAQAA" in 
        #     b"".join(self.do(bytes(range(0, 256)))),
        #     "All bytes produced innacurate results")

        # Test execution
        test = string.ascii_letters + string.digits
        testcmd = "Write-Output '%s'" % test
        encoded = b"".join(self.do(testcmd.encode()))
        cmd = "pwsh -c \"%s\"" % encoded.decode()

        with self.Container(
            image="mcr.microsoft.com/powershell:latest",
            network_disabled=True,
            command=cmd) as container:

            # Fetch output
            output = [line.strip() for line in container.logs(stdout=True, stderr=True)][0]

            # Wait for container to cleanup
            container.wait()

            # Verify execution was successful
            self.assertEqual(output.decode(), test, "Execution produced inaccurate results")
