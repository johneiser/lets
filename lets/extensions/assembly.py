from lets.extensions.docker import DockerExtension


class AssemblyExtension(DockerExtension):
    """
    Extend a module with specific utilities for assembling code.
    """

    @DockerExtension.ImageDecorator(["local/tools/keystone:latest"])
    def assemble(self, code:str, arch:str, mode:str) -> bytes:
        """
        Assemble the provided code according to the specified architecture.

        :param code: Code to be assembled, as str
        :param arch: Architecture for which to assemble
        :param mode: Mode with which the architecture operates
        :return: Assembled bytes
        """

        # Remove comments
        code = "\n".join([c.strip().split(";")[0].strip() for c in code.strip().split("\n")])

        # Build command
        cmd = "python assemble.py /data/in %s %s /data/out" % (arch, mode)

        # Prepare input and output files
        with self.IO(code.encode(), infile="/data/in", outfile="/data/out") as io:

            # Prepare container with input file and output file
            # mounted as volumes
            with self.Container(
                image="local/tools/keystone:latest",
                network_disabled=True,
                volumes=io.volumes,
                command=cmd) as container:

                # Handle container stdout and stderr
                for line in container.logs(stdout=True, stderr=True):
                    self.info(line.strip().decode(), decorate=False)

                # Handle data written to output file
                container.wait()
                return io.outfile.read()

class DisassemblyExtension(DockerExtension):
    """
    Extend a module with specific utilities for disassembling code.
    """

    @DockerExtension.ImageDecorator(["local/tools/capstone:latest"])
    def disassemble(self, data:bytes, arch:str, mode:str) -> str:
        """
        Disassemble the provided code according to the specified architecture.

        :param code: Data to be disassembled, as bytes
        :param arch: Architecture for which to disassemble
        :param mode: Mode with which the architecture operates
        :return: Disassembled code, as str
        """

        # Build command
        cmd = "python disassemble.py /data/in %s %s /data/out" % (arch, mode)

        # Prepare input and output files
        with self.IO(data, infile="/data/in", outfile="/data/out") as io:

            # Prepare container with input file and output file
            # mounted as volumes
            with self.Container(
                image="local/tools/capstone:latest",
                network_disabled=True,
                volumes=io.volumes,
                command=cmd) as container:

                # Handle container stdout and stderr
                for line in container.logs(stdout=True, stderr=True):
                    self.info(line.strip().decode(), decorate=False)

                # Handle data written to output file
                container.wait()
                return io.outfile.read()
