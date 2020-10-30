from lets.__module__ import Module, TestCase
import base64


class Base64(Module):
    """
    Base64 decode the provided data.
    """

    def handle(self, input):
        for data in input:
            yield base64.b64decode(data)


class Base64Tests(TestCase):

    def test_all_bytes(self):
        test = b"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=="
        result = self.module(test)
        self.assertEqual(
            result,
            bytes(range(0,256)),
            "All bytes produced inaccurate results")
