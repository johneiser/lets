import os, sys, argparse, logging, unittest, subprocess, warnings
import lets
from lets.module import Module


class BashInterfaceTest(unittest.TestCase):
    """
    Test the bash interface.  Relies on the following modules:

    ["encode/base64"]
    """
    def test(self):
        """
        Perform unit tests to verify the bash interface functionality.
        """
        _lets = os.path.sep.join([os.path.abspath(os.path.dirname(__file__)), "..", "lets.py"])

        p = subprocess.Popen(["python3", _lets, "encode/base64"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = p.communicate(input=b"abcd")
        self.assertEqual(
            out,
            b"YWJjZA==",
            "Base64 encoding produced inaccurate results")


class PythonInterfaceTest(unittest.TestCase):
    """
    Test the python interface.  Relies on the following modules:

    ["encode/base64"]
    """
    def test(self):
        """
        Perform unit tests to verify the python interface functionality.
        """

        self.assertEqual(
            lets.do("encode/base64", b"abcd", {"verbose" : False}),
            b"YWJjZA==",
            "Base64 encoding produced inaccurate bytes")

        self.assertEqual(
            b"".join(lets.do("encode/base64", b"abcd", {"verbose" : False}, generate=True)),
            b"YWJjZA==",
            "Base64 encoding produced inaccurate generator")


def test_suite(module:str=None):
    """
    Retrieve tests present in the framework.

    :param module: Specify a single test to be retrieved
    :return: TestSuite containing test(s)
    """

    # Initialize test suite
    suite = unittest.TestSuite()

    if module:
        try:
            # Build module and add test
            mod = Module.build(module)
            if mod and hasattr(mod, Module.test_method):
                suite.addTest(mod)
            else:
                raise(Module.Exception("Error loading module: %s" % module))
        except Module.Exception as e:
            logging.error("[!] %s" % (str(e)))

    else:
        # Add interface tests
        suite.addTest(BashInterfaceTest(Module.test_method))
        suite.addTest(PythonInterfaceTest(Module.test_method))

        try:
            # Walk modules and add tests
            for mod in Module.build_all():
                if mod and hasattr(mod, Module.test_method):
                    suite.addTest(mod)
        except Module.Exception as e:
            logging.error("[!] %s" % (str(e)))

    return suite

def test(module:str=None):
    """
    Perform tests present in the framework.

    :param module: Specify a single test to be run   
    """
    # Execute test suite
    runner = unittest.TextTestRunner()
    runner.run(test_suite(module))
