""" lets/sample/mydockermodule.py """

from lets.__module__ import Module, Container, Mount


class MyDockerModule(Module):
    """
    Open input data in an interactive hex editor
    before passing it along.

    Example:
    $ echo 'test' | lets sample/mydockermodule | xxd
    """
    images = ["local/sample"]
    
    def handle(self, input):
        assert input is not None, "Must provide data as input"

        for data in input:
            self.log.debug("Opening %d bytes in a hex editor", len(data))

            # Build a mount and write the input data
            with Mount(path="/data") as mount:
                with mount.open("input", "wb") as f:
                    f.write(data)

                # Build a docker container with mount and
                # execute `hexedit` on the data
                with Container.run(
                    image="local/sample",
                    volumes=mount.volumes,
                    command="hexedit /data/input",
                    stdin_open=True,
                    tty=True) as container:

                    # Interact with the container
                    container.interact()

                # Retrieve and `yield` the resulting data
                with mount.open("input", "rb") as f:
                    yield f.read()

