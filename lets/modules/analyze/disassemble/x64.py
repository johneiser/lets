from lets.module import Module
from lets.extensions.docker import DockerExtension

import unittest

class X64(DockerExtension, Module):
    """
    Disassemble bytes into x86_64 assembly with an interactive radare2 console.
    """
    interactive = True

    # A list of docker images required by the module.
    images = [
        "tools/radare2:latest"
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
        super().do(data, options)

        # Validate input
        try:
            assert data, "Expecting data"
        except AssertionError as e:
            self.throw(e)

        # Build command
        cmd = "r2 -a x86 -b 32 -c Vp /data/in" # -A

        # Prepare input and output files
        with self.IO(data, infile="/data/in", outfile="/data/out") as io:

            # Prepare container with input file and output file
            # mounted as volumes
            with self.Container(
                image="tools/radare2:latest",
                network_disabled=True,
                volumes=io.volumes,
                stdin_open=True,
                tty=True,
                command=cmd) as container:

                container.interact()

    @unittest.skip("Interactive, no tests.")
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        pass