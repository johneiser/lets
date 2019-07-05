from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import zlib, base64, string

class Compress(DockerExtension, Module):
    """
    Compress and Base64 encode a python script and prepend a decode/decompress stub.
    """

    # A list of docker images required by the module.
    images = [
        "python:2",
        "python:3"
    ]

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

        DockerExtension.do prepares required docker images.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        super().do(data, options, prep=False)

        # Validate input
        try:
            assert data, "Expecting data"
        except AssertionError as e:
            self.throw(e)

        # Compress command
        compressed = zlib.compress(data, level=9)

        # Encode command
        encoded = base64.b64encode(compressed)
        self.options["encoded"] = encoded.decode()
        
        # Place encoded command in harness
        cmd = "import base64,sys,zlib;exec(zlib.decompress(base64.b64decode({2:str,3:lambda b:bytes(b,'UTF-8')}[sys.version_info[0]]('%(encoded)s'))))" % self.options

        # Convert harness to bytes and return
        yield cmd.encode()

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test encoding
        self.assertTrue(
            b"eNoBAAH//gABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v+t9n+B" in 
            b"".join(self.do(bytes(range(0, 256)))),
            "All bytes produced innacurate results")

        # Test execution
        test = string.ascii_letters + string.digits
        testcmd = "print('%s')" % test
        encoded = b"".join(self.do(testcmd.encode()))
        cmd = "python -c \"%s\"" % encoded.decode()

        with self.Container(
            image="python:2",
            network_disabled=True,
            command=cmd) as container:

            # Fetch output
            output = [line.strip() for line in container.logs(stdout=True, stderr=True)][0]

            # Wait for container to cleanup
            container.wait()

            # Verify execution was successful
            self.assertEqual(output.decode(), test, "Version 2 execution produced inaccurate results")

        with self.Container(
            image="python:3",
            network_disabled=True,
            command=cmd) as container:

            # Fetch output
            output = [line.strip() for line in container.logs(stdout=True, stderr=True)][0]

            # Wait for container to cleanup
            container.wait()

            # Verify execution was successful
            self.assertEqual(output.decode(), test, "Version 3 execution produced inaccurate results")
