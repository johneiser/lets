from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import os, zlib, base64, string
from Crypto.Cipher import ARC4
from Crypto.Hash import SHA256


class RC4(DockerExtension, Module):
    """
    Compress, RC4 encrypt and Base64 encode a python script and prepend a
    decode/decrypt/decompress stub.
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
        compressed = zlib.compress(data, level=9)

        # Encrypt command
        encrypted = ARC4.new(key).encrypt(compressed)

        # Encode command
        encoded = base64.b64encode(encrypted)
        self.options["encoded"] = encoded.decode()

        # Encode key
        encoded_key = base64.b64encode(key)
        self.options["encoded_key"] = encoded_key.decode()

        # Build RC4

        # def rc4(d:int[], k:int[]) -> int[]
        # """
        # Encrypt/Decrypt an array of bytes using RC4.
        # 
        # :param d: Data to encrypt/decrypt
        # :param k: Key to use for encryption/decryption
        # :return: Bytes encrypted/decrypted
        # """
        rc4 = """S,j,o=list(range(256)),0,[]
for i in list(range(256)):
    j=(j+S[i]+k[i%len(k)])%256
    S[i],S[j]=S[j],S[i]
i=j=0
for b in d:
    i=(i+1)%256
    j=(j+S[i])%256
    S[i],S[j]=S[j],S[i]
    K=S[(S[i]+S[j])%256]
    o.append(b^K)"""

        self.options["encoded_rc4"] = base64.b64encode(rc4.encode()).decode()

        # Place rc4 and encoded command in harness
        cmd = ("import base64,sys,zlib;"+

            # Determine whether version requires the use of `ord`
            "f={2:ord,3:lambda b:b}[sys.version_info[0]];"+

            # Store encrypted data and key in dictionary
            "v={'d':[f(b) for b in base64.b64decode('%(encoded)s')],'k':[f(b) for b in base64.b64decode('%(encoded_key)s')]};"+

            # Execute RC4 decryption with encrypted data and key in locals
            "exec(base64.b64decode('%(encoded_rc4)s'),globals(),v);"+

            # Decompress and execute now decrypted data
            "exec(zlib.decompress(bytes(bytearray(v.get('o')))));"

            ) % self.options

        # Convert harness to bytes and return
        yield cmd.encode()

    @DockerExtension.ImageDecorator(["python:2", "python:3"])
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
        testcmd = "print('%s')" % test
        encoded = b"".join(self.do(testcmd.encode()))
        cmd = encoded.decode()

        with self.Container(
            image="python:2",
            network_disabled=True,
            entrypoint=["python", "-c"],
            command=[cmd]) as container:

            # Fetch output
            output = [line.strip() for line in container.logs(stdout=True, stderr=True)][0]

            # Wait for container to cleanup
            container.wait()

            # Verify execution was successful
            self.assertEqual(output.decode(), test, "Version 2 execution produced inaccurate results")

        with self.Container(
            image="python:3",
            network_disabled=True,
            entrypoint=["python", "-c"],
            command=[cmd]) as container:

            # Fetch output
            output = [line.strip() for line in container.logs(stdout=True, stderr=True)][0]

            # Wait for container to cleanup
            container.wait()

            # Verify execution was successful
            self.assertEqual(output.decode(), test, "Version 3 execution produced inaccurate results")
