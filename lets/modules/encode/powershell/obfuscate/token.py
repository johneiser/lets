from lets.module import Module
from lets.extensions.docker import DockerExtension

# Imports required to execute this module
import base64, string


class Token(DockerExtension, Module):
    """
    Obfuscate a powershell script with token-based manipulation.
    """
    TECHNIQUES = [
        "STRING,1",     # Concatenate --> e.g. ('co'+'ffe'+'e')
        "STRING,2",     # Reorder     --> e.g. ('{1}{0}'-f'ffee','co')

        "COMMAND,1",    # Ticks                   --> e.g. Ne`w-O`Bject
        "COMMAND,2",    # Splatting + Concatenate --> e.g. &('Ne'+'w-Ob'+'ject')
        "COMMAND,3",    # Splatting + Reorder     --> e.g. &('{1}{0}'-f'bject','New-O')

        "ARGUMENT,1",   # Random Case --> e.g. nEt.weBclIenT
        "ARGUMENT,2",   # Ticks       --> e.g. nE`T.we`Bc`lIe`NT
        "ARGUMENT,3",   # Concatenate --> e.g. ('Ne'+'t.We'+'bClient')
        "ARGUMENT,4",   # Reorder     --> e.g. ('{1}{0}'-f'bClient','Net.We') 

        "MEMBER,1",     # Random Case --> e.g. dOwnLoAdsTRing
        "MEMBER,2",     # Ticks       --> e.g. d`Ow`NLoAd`STRin`g
        "MEMBER,3",     # Concatenate --> e.g. ('dOwnLo'+'AdsT'+'Ring').Invoke()
        "MEMBER,4",     # Reorder     --> e.g. ('{1}{0}'-f'dString','Downloa').Invoke()

        "VARIABLE,1",   # Random Case + {} + Ticks --> e.g. ${c`hEm`eX}

        "TYPE,1",       # Type Cast + Concatenate --> e.g. [Type]('Con'+'sole')
        "TYPE,2",       # Type Cast + Reordered   --> e.g. [Type]('{1}{0}'-f'sole','Con')

        "COMMENT,1",    # Remove Comments   --> e.g. self-explanatory

        "WHITESPACE,1", # Random Whitespace --> e.g. .( 'Ne'  +'w-Ob' +  'ject')

        "ALL,1",        # Execute ALL Token obfuscation techniques (random order)
    ]

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant
        to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Specify technique
        parser.add_argument("-t", "--technique",
            help="technique to use in obfuscation",
            type=str,
            choices=self.TECHNIQUES,
            default="ALL,1")

        return parser

    @DockerExtension.ImageDecorator(["local/tools/invoke-obfuscation:latest"])
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
            technique = self.options.get("technique")
            assert technique in self.TECHNIQUES, "Invalid technique: %s (%s)" % (technique, str(self.TECHNIQUES))
        except AssertionError as e:
            self.throw(e)

        # Build command
        cmd = "Invoke-Obfuscation -Quiet -ScriptPath /data/in -Command 'TOKEN,%(technique)s' | Out-File /data/out" % self.options

        # Prepare input and output files
        with self.IO(data,
            infile="/data/in", outfile="/data/out") as io:

            # Prepare container with input file and output file
            # mounted as volumes
            with self.Container(
                image="local/tools/invoke-obfuscation:latest",
                network_disabled=True,
                volumes=io.volumes,
                entrypoint=["pwsh", "-c"],
                command=[cmd]) as container:

                # Handle container stdout and stderr
                for line in container.logs(
                    stdout=True, stderr=True):
                    self.info(line.strip().decode(), decorate=False)

                # Handle data written to output file
                container.wait()
                yield io.outfile.read()

    @DockerExtension.ImageDecorator(["local/tools/invoke-obfuscation:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test encoding
        for technique in self.TECHNIQUES:
            test = string.ascii_letters + string.digits
            testcmd = "Write-Output '%s'" % test
            encoded = b"".join(self.do(testcmd.encode(), {"technique" : technique}))
            self.assertTrue(len(encoded) > 0, "Technique %s produced inaccurate results" % technique)

            # Base64 encode to get past the container layer
            cmd = base64.b64encode(encoded.decode().encode("utf-16-le")).decode()

            # Test execution
            with self.Container(
                image="local/tools/invoke-obfuscation:latest",
                network_disabled=True,
                environment={
                    "comspec" : "C:\\Windows\\system32\\cmd.exe",
                },
                entrypoint=["pwsh", "-e"],
                command=[cmd]) as container:

                # Fetch output
                output = [line.strip() for line in container.logs(stdout=True, stderr=True)][0]

                # Wait for container to cleanup
                container.wait()

                # Verify execution was successful
                self.assertEqual(output.decode(), test, "Execution of technique %s produced inaccurate results" % technique)
