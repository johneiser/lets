from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import base64, string


class Bash(DockerExtension, Module):
    """
    Format python code into a bash command.
    """

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
            default="python")

        # Target specification
        parser.add_argument("-p", "--platform",
            help="specify the intended target platform",
            type=str,
            choices=["linux", "osx"],
            default="linux")

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

        # Encode command
        encoded = base64.b64encode(data)
        self.options["encoded"] = encoded.decode()
        
        # Place encoded command in harness
        platform = self.options.get("platform")
        if platform and platform.lower() == "linux":
            cmd = "echo '%(encoded)s'|base64 -d|%(shell)s" % self.options
        elif platform and platform.lower() == "osx":
            cmd = "echo '%(encoded)s'|base64 -D|%(shell)s" % self.options
        else:
            self.throw(Exception("Invalid platform: %s" % platform))

        # Convert harness to bytes and return
        yield cmd.encode()

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test encoding
        self.assertTrue(
            b"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==" in 
            b"".join(self.do(bytes(range(0, 256)))),
            "All bytes produced innacurate results")

        # Test execution (TODO)
            