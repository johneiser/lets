#!/usr/bin/env python3
import os, sys, argparse, unittest, subprocess
import lets

class BashInterfaceTest(unittest.TestCase):
    """
    Test the bash interface.  Relies on the following modules:

    ["encode/base64"]
    """
    def test(self):
        """
        Perform unit tests to verify the bash interface functionality.
        """
        _lets = os.path.sep.join([os.path.abspath(os.path.dirname(__file__)), "lets.py"])

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Lets-Test :: Testing A Modular Framework for Arbitrary Action",
        usage="%(prog)s [module]"
        )
    parser.add_argument("module", metavar="module", type=str, help="module to use", nargs="?")
    args = parser.parse_args()

    # Initialize test suite
    suite = unittest.TestSuite()

    if args.module:
        # Build module and add test
        mod = lets.module.Module.build(args.module)
        if mod:
            suite.addTest(mod)
        else:
            raise(lets.module.Module.Exception("Error loading module: %s" % args.module))

    else:
        # Add interface tests
        suite.addTest(BashInterfaceTest(lets.module.Module.test_method))
        suite.addTest(PythonInterfaceTest(lets.module.Module.test_method))

        # Walk modules and add tests
        for mod in lets.module.Module.build_all():
            if mod and hasattr(mod, lets.module.Module.test_method):
                suite.addTest(mod)

    # Execute test suite
    runner = unittest.TextTestRunner()
    runner.run(suite)