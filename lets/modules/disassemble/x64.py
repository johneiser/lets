from lets.module import Module
from lets.extensions.assembly import DisassemblyExtension

# Imports required to execute this module
import os, base64

class X64(DisassemblyExtension, Module):
    """
    Disassemble bytes into x86_64 assembly code.
    """

    # A list of docker images required by the module.
    images = [
        "local/tools/capstone:latest"
    ]

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

        # Disassemble
        yield self.disassemble(data, arch="X86", mode="64")

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test production of results
        sc = b"".join(self.do(b"\x90"))
        self.assertGreater(len(sc),
            0,
            "NOP produced no results")