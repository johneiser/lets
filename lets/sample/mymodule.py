""" lets/sample/mymodule.py """

from lets.__module__ import Module


class MyModule(Module):
    """
    Flip input data in reverse.
    """

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("-c", "--count", type=int,
            help="number of bytes in each chunk", default=1)

    def handle(self, input, count):
        assert input is not None, "Must provide data as input"

        for data in input:
            self.log.debug("Flipping %i bytes by %i", len(data), count)

            # Perform the flipping, then `yield` the result.
            n = len(data)
            i = 0
            b = b""
            while i < n:
                b += data[max(0,n-i-count):max(0,n-i)]
                i += count
            yield b

