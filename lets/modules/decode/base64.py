from lets.module import Module
from lets.logger import log
from unittest import TestCase
import base64

class Base64(Module):
    """
    Base64 decode input data.
    """
    def do(self, **kwargs):
        assert self.has_input(), "Must provide input data"

        for data in self.get_input():
            yield base64.b64decode(data)

class Base64Tests(TestCase):
    """
    Ensure base64 encoded data is accurate
    """
    def test_all_bytes(self):
        test = b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        mod = Base64(input=test)
        out = next(mod.do())
        self.assertEqual(
            bytes(range(0,256)),
            out,
            "All bytes produced inaccurate results")
