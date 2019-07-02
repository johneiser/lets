from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import base64, string

class Base64(DockerExtension, Module):
    """
    Base64 encode a bash script and prepend a decode stub.
    """

    # A list of docker images required by the module.
    images = [
        "debian:latest"
    ]

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Customize shell
        parser.add_argument("-s", "--shell",
            help="use the specified shell",
            type=str,
            default="/bin/bash")

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
        super().do(data, options)

        # Validate input
        try:
            assert data, "Expecting data"
        except AssertionError as e:
            self.throw(e)

        # Encode command
        self.options["encoded"] = base64.b64encode(data).decode()
        
        # Place encoded command in harness
        cmd = "echo '%(encoded)s'|base64 --decode|%(shell)s" % self.options

        # Convert harness to bytes and return
        yield cmd.encode()

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test encoding
        self.assertEqual(
            b"".join(self.do(bytes(range(0,256)))),
            b"echo 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='|base64 --decode|/bin/bash",
            "All bytes produced inaccurate results")

        # Test execution
        test = string.ascii_letters + string.digits
        testcmd = "echo '%s'" % test
        encoded = b"".join(self.do(testcmd.encode()))
        cmd = "bash -c \"%s\"" % encoded.decode()

        with self.Container(
            image="debian:latest",
            network_disabled=True,
            command=cmd) as container:

            # Fetch output
            output = [line.strip() for line in container.logs(stdout=True, stderr=True)][0]

            # Wait for container to cleanup
            container.wait()

            # Verify execution was successful
            self.assertEqual(output.decode(), test, "Execution produced inaccurate results")
            