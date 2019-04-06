from lets.docker import DockerModule

# Imports required to execute this module
import os, base64, tempfile

class MyDockerModule(DockerModule):
    """
    [Description of what type of data this module expects, what configuration options
    it accepts, what type of execution it performs, and what data it produces, if any].

    [Notes and warnings]

    [Author and credits]
    """

    # A list of docker images required by the module.
    images = [
        "ubuntu:latest"
    ]

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Enable convert before encode
        parser.add_argument("-u", "--upper",
            help="convert to uppercase before encoding",
            action="store_true",
            default=False)

        return parser

    def do(self, data:bytes, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        DockerModule.do prepares required docker images.

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

        # Convert, if necessary
        if self.options.get("upper"):
            try:
                self.info("Converting to uppercase")
                data = data.decode().upper().encode()
            except UnicodeDecodeError as e:
                self.throw(e)

        # Prepare input file
        with tempfile.NamedTemporaryFile(dir="/tmp") as infile:
            infile.write(data)
            infile.seek(0)

            # Prepare output file
            with tempfile.NamedTemporaryFile(dir="/tmp") as outfile:

                # Prepare container with input file and output file
                # mounted as volumes
                with self.Container(
                    image="ubuntu:latest",
                    volumes={
                        infile.name : {
                            "bind" : "/data/in",
                            "mode" : "ro"
                        },
                        outfile.name : {
                            "bind" : "/data/out",
                            "mode" : "rw"
                        }
                    },
                    command="cp /data/in /data/out") as container:

                    # Handle container stdout and stderr
                    for line in container.logs(stdout=True, stderr=True):
                        self.info(line.strip().decode(), decorate=False)

                    # Handle data written to output file
                    container.wait()
                    yield base64.b64encode(outfile.read())

        return iter(())

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test generic
        self.assertEqual(
            b"".join(self.do(b"abcd", {"upper" : False})),
            b"YWJjZA==",
            "Defaults produced inaccurate results")

        # Test with uppercase conversion
        self.assertEqual(
            b"".join(self.do(b"abcd", {"upper" : True})),
            b"QUJDRA==",
            "Uppercase produced inaccurate results")