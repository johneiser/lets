""" modules/sample/mydockermodule.py """

from lets.module import Module
from lets.logger import log
from lets.extensions.docker import IO, Container, ImageDecorator
from unittest import TestCase

# Our module inherits `Module` and is named the same
# as its file (case-insensitive). We include a
# description of the module in the docustring, below.
class MyDockerModule(Module):
    """
    Open input data in an interactive hex editor
    before passing it along.

    Example:
    $ echo 'test' | lets sample/mydockermodule | xxd
    """
    
    # Note: no additional arguments are necessary, so 
    # we skip implementing the `add_arguments` function.

    # We use the `ImageDecorator` to ensure our custom
    # docker image is built and ready by the time we
    # execute.
    @ImageDecorator("local/sample")
    def do(self, **kwargs):

        # We make sure we have data to work with before starting.
        assert self.has_input(), "Must provide input data"

        # We fetch data from the input generator.
        for data in self.get_input():
            log.debug("Opening %d bytes in a hex editor", len(data))

            # We use the IO docker extension to load the input
            # data in the container at "/data/input".
            with IO(mount="/data") as io:
                with io.open("input", "wb") as f:
                    f.write(data)

                # We build a docker container with our IO volume
                # mounted to execute `hexedit` on our input.
                with Container(
                    image="local/sample",
                    volumes=io.volumes,
                    command="hexedit /data/input",
                    stdin_open=True,
                    tty=True,
                ) as container:

                    # We connect to the container, then wait for
                    # it to finish saving.
                    container.interact()
                    container.wait()

                # We grab the new data and `yield` it as output.
                with io.open("input", "rb") as f:
                    yield f.read()
                
# To ensure our module works as expected, we include
# a set of unit tests to cover the range of potential
# behavior. In this case, the functionality is
# interactive, so there is not much we can do besides
# verify the container can be built and the tools
# are accessible.
class MyDockerModuleTests(TestCase):
    """
    Example: Ensure MyDockerModule works as expected.
    """

    @ImageDecorator("local/sample")
    def test_image(self):
        """
        Confirm image can be built and tools are present.
        """
        with Container(
            image="local/sample",
            command="which hexedit",
        ) as container:
            out = container.logs()
            container.wait()
            self.assertEqual(b"/usr/bin/hexedit\n", out,
                "Container not functional: local/sample")
