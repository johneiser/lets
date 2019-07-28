from lets.module import Module

# Imports required to execute this module
import string
from Crypto.Cipher import ARC4
from Crypto.Hash import SHA256


class RC4(Module):
    """RC4 encrypt/decrypt a string of bytes."""

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant
        to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Set encryption parameters
        parser.add_argument("-k", "--key",
            help="key used for RC4 encryption",
            type=str,
            required=True)

        return parser

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
            assert self.options.get("key"), "Key required"
        except AssertionError as e:
            self.throw(e)

        # Normalize key
        key = SHA256.new(self.options.get("key").encode()).digest()

        # Encrypt data
        yield ARC4.new(key).encrypt(data)

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        self.assertEqual(
            b"".join(self.do(bytes(range(0,256)), {"key": string.printable})),
            (
                b'\x76\x14\x25\x52\x2d\xd8\x7a\xf8\xcf\xec\xb5\x4b\x1d\xab\x10\x70'+
                b'\x95\x36\x6a\xde\x7e\x9e\x93\x05\xd3\xad\x07\xf5\xae\x5b\xe6\x0e'+
                b'\xbd\xdf\xc0\x65\x21\x66\xc2\x67\x7c\xe7\xb6\x28\xb8\xe9\x4a\x61'+
                b'\xde\x85\xf8\xb1\xfe\x8f\x16\xa5\xa8\x94\xae\x8c\x65\x19\xe4\xf4'+
                b'\xf2\x3d\xcc\xd5\x89\x04\xcf\xec\x9f\x54\x3f\x96\x84\x0b\xb9\xf8'+
                b'\x7f\x08\x0a\xf8\x4b\xd3\xf6\x30\x5b\x73\x5a\x71\x38\x36\x62\x01'+
                b'\x36\xb7\x66\x1a\x49\x9f\xb5\x85\x86\x5c\xe4\xde\xac\x43\xb6\x21'+
                b'\xd4\xb7\xb2\x6a\xb4\x17\xae\x4c\x87\xe0\x5f\xd0\x02\x72\xdd\xd5'+
                b'\x4d\x41\xa2\xf3\x11\xc7\x77\x4c\x8c\x87\xe3\xa2\x54\xbf\x35\xa8'+
                b'\x12\x60\xda\x7b\xa4\x90\x63\x2c\x79\xf0\x9a\x5e\xec\x65\x80\x1c'+
                b'\x05\x22\x08\x3c\x93\xb6\xd9\x45\xae\xd7\x9e\x83\x34\x4b\x2d\xff'+
                b'\x1b\x44\xe9\xfd\x86\x44\x14\xfc\x4e\x07\x26\x9b\x08\xa7\x6d\xb5'+
                b'\x23\xe6\x06\x88\xc0\x4f\x2d\xe0\xb8\xdb\x49\xb6\x7c\x8f\xa5\xc3'+
                b'\x08\x7a\x71\x08\x8d\x13\x67\x8a\x7e\x59\x83\xf1\xb4\xfa\xb0\xe3'+
                b'\xa6\x91\x78\x8e\x15\x7f\x75\x29\xa0\xf1\xba\xa9\x90\x19\xdd\x07'+
                b'\xbd\x46\xa2\x36\x03\xdb\xcb\x95\xbf\x73\xcc\xf4\x63\x44\x34\x5c'
            ),
            "All bytes with printable string produced inaccurate results")
