""" modules/sample/mymodule.py """

from lets.module import Module
from lets.logger import log
from unittest import TestCase

# Our module inherits `Module` and is named the same
# as its file (case-insensitive). We include a
# description of the module in the docustring, below.
class MyModule(Module):
    """
    Flip input data in reverse.
    """

    # We add a single argument, `count`, as an integer
    # of default value 1.
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("-c", "--count",
            help="number of bytes in each chunk",
            type=int, default=1)

    # We include our argument `count` in the `do` function
    # definition.
    def do(self, count, **kwargs):

        # We make sure we have data to work with before starting.
        assert self.has_input(), "Must provide input data"

        # We fetch data from the input generator.
        for data in self.get_input():
            log.debug("Flipping %d bytes by %d", len(data), count)

            # We perform the flipping, then `yield` the result.
            n = len(data)
            i = 0
            b = b""
            while i < n:
                b += data[max(0,n-i-count):max(0,n-i)]
                i += count
            yield b

# To ensure our module works as expected, we include
# a set of unit tests to cover the range of potential
# behavior.
class MyModuleTests(TestCase):
    """
    Example: Ensure MyModule works as expected.
    """
    def test_flip_all_bytes(self):
        """
        Verify basic accuracy.
        """
        test = bytes(range(0,256,1))
        mod = MyModule(input=test)
        out = next(mod.do(count=1))
        self.assertEqual(bytes(range(255,-1,-1)), out,
            "Flipped all bytes by 1 produced inaccurate results")

    def test_flip_by_2(self):
        """
        Verify accuracy with a minority chunk size.
        """
        test = b"abcdefgh"
        mod = MyModule(input=test)
        out = next(mod.do(count=2))
        self.assertEqual(b"ghefcdab", out,
            "Flip bytes by 2 produced inaccurate results")

    def test_flip_by_most(self):
        """
        Verify accuracy with a majority chunk size.
        """
        test = b"abcdefgh"
        mod = MyModule(input=test)
        out = next(mod.do(count=7))
        self.assertEqual(b"bcdefgha", out,
            "Flip bytes by most produced inaccurate results")
    
    def test_flip_by_all(self):
        """
        Flipping by the length of the input
        should match the original.
        """
        test = b"abcdefgh"
        mod = MyModule(input=test)
        out = next(mod.do(count=len(test)))
        self.assertEqual(test, out,
            "Flip bytes by all does not match original")

    def test_flip_by_more(self):
        """
        Flipping by more then the length of the
        input should match the original.
        """
        test = b"abcdefgh"
        mod = MyModule(input=test)
        out = next(mod.do(count=9))
        self.assertEqual(test, out,
            "Flip bytes by more does not match original")