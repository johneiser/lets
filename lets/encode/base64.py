from lets.__module__ import Module, TestCase
import base64


class Base64(Module):
    """
    Base64 encode the provided data.
    """

    def handle(self, input):
        assert input is not None, "Must provide data as input"
        for data in input:
            yield base64.b64encode(data)


class Base64Tests(TestCase):

    def test_all_bytes(self):
        test = bytes(range(0,256))
        result = self.module(test)
        self.assertEqual(
            result,
            b"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==",
            "All bytes produced inaccurate results")
