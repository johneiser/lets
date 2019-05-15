from django.test import TestCase

class DoViewTests(TestCase):

    def test_valid_module(self):
        """
        Verify whether the rest api will properly handle the
        execution of a valid module.
        """
        response = self.client.post(
            "/lets/encode/base64",
            b"abcd",
            "text/plain; charset=utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b"YWJjZA==",
            "Base64 encoding produced inaccurate results")

    def test_invalid_module(self):
        """
        Verify that the rest api will properly handle an
        invalid module
        """

        response1 = self.client.post(
            "/lets/bad/module",
            b"1234",
            "text/plain; charset=utf-8")

        self.assertEqual(response1.status_code, 404)

        response2 = self.client.get("/lets/encode/base64")

        self.assertEqual(response2.status_code, 404)
