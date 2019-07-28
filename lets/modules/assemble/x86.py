from lets.module import Module
from lets.extensions.assembly import AssemblyExtension


class X86(AssemblyExtension, Module):
    """
    Assemble x86 code into bytes.
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

        try:
            # Convert to str
            code = data.decode()
        except UnicodeDecodeError as e:
            self.throw(e)

        # Assemble
        yield self.assemble(code, arch="X86", mode="32")

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test basic instructions
        code = """
xor ebx, ebx    ; Comments
xchg eax, ebx   ; are
sub eax, 10
jnz there       ;

here:
int 3           ; fun!

there:
    add esp, 0x12
ret
"""
        self.assertEqual(
            b"".join(self.do(code.encode())),
            b"\x31\xdb\x93\x83\xe8\x0a\x75\x02\xcd\x03\x83\xc4\x12\xc3")