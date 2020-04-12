"""
Perfom unit tests found in the framework.

Usage: 

Run all tests from the commandlind
$ python -m unittest lets

Run a single module's tests from the commandline
$ python -m unittest lets.modules.encode.base64

Run all tests from python
> import lets
> lets.test()

Run a single module's tests from python
> import lets
> lets.test("encode/base64")
"""
import os, unittest, logging
from .module import load, load_all
from .logger import handler

class BashInterfaceTests(unittest.TestCase):
    """
    Ensure data passing through the bash interface is accurate.
    """

    #
    # help
    #

    def test_help(self):
        import subprocess
        p = subprocess.Popen(["lets", "-h"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = p.communicate()
        self.assertTrue(out.startswith(b"usage: lets"))

    def test_module_help(self):
        import subprocess
        p = subprocess.Popen(["lets", "encode/base64", "-h"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = p.communicate()
        self.assertTrue(out.startswith(b"usage: base64"))

    #
    # do
    #

    def test_do_input_bytes(self):
        import subprocess, base64
        test = bytes(range(0,256))
        p = subprocess.Popen(["lets", "encode/base64"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = p.communicate(input=test)
        self.assertEqual(out, base64.b64encode(test),
            "Input from bytes produced inaccurate results")

    def test_do_input_file(self):
        import subprocess, tempfile, base64
        test = bytes(range(0,256))
        with tempfile.NamedTemporaryFile("wb") as w:
            w.write(test)
            w.seek(0)
            p = subprocess.Popen("lets encode/base64 < %s" % w.name, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out,err = p.communicate()
            self.assertEqual(out, base64.b64encode(test),
                "Input from file produced inaccurate results")

class PythonInterfaceTests(unittest.TestCase):
    """
    Ensure data passing through the python interface is accurate.
    """

    #
    # lets.help
    #

    def test_help(self):
        import lets
        out = lets.help()
        self.assertIsNotNone(out, "Failed to produce help text")
        self.assertTrue(out.startswith("usage: lets"), "Invalid help text")

    def test_module_help(self):
        import lets
        out = lets.help("encode/base64")
        self.assertIsNotNone(out, "Failed to produce module help text")
        self.assertTrue(out.startswith("usage: base64"), "Invalid module help text")

    def test_module_help_not_found(self):
        import lets
        with self.assertRaises(ModuleNotFoundError):
            lets.help("")

    def test_module_help_bad_module(self):
        import lets
        with self.assertRaises(TypeError):
            lets.help(b"")

    #
    # lets.usage
    #

    def test_usage(self):
        import lets
        out = lets.usage()
        self.assertIsNotNone(out, "Failed to produce usage text")
        self.assertTrue(out.startswith("usage: lets"), "Invalid usage text")

    def test_module_usage(self):
        import lets
        out = lets.usage("encode/base64")
        self.assertIsNotNone(out, "Failed to produce module usage text")
        self.assertTrue(out.startswith("usage: base64"), "Invalid module usage text")

    def test_module_usage_not_found(self):
        import lets
        with self.assertRaises(ModuleNotFoundError):
            lets.usage("")

    def test_module_usage_bad_module(self):
        import lets
        with self.assertRaises(TypeError):
            lets.usage(b"")

    #
    # lets.do
    #

    def test_do_module_not_found(self):
        import lets
        with self.assertRaises(ModuleNotFoundError):
            lets.do("")

    def test_do_bad_module(self):
        import lets
        with self.assertRaises(TypeError):
            lets.do(b"")

    def test_do_no_module(self):
        import lets
        with self.assertRaises(TypeError):
            lets.do(None)

    def test_do_bad_input(self):
        import lets, io
        with self.assertRaises(TypeError):
            with io.StringIO() as s:
                lets.do("encode/base64", input=s)

    def test_do_no_input(self):
        import lets
        with self.assertRaises(AssertionError):
            lets.do("encode/base64")

    #
    # lets.do input bytes
    #

    def test_do_input_bytes(self):
        """
        lets.do should be able to handle bytes as input.
        """
        import lets, base64
        test = bytes(range(0,256))
        out = lets.do("encode/base64", input=test)
        self.assertEqual(out, base64.b64encode(test),
            "Input from bytes produced inaccurate results")

    def test_do_input_bytes_iterate(self):
        """
        lets.do should be able to handle bytes as input with iterate.
        """
        import lets, base64
        test = b"abcd\nefgh\n"
        out = lets.do("encode/base64", input=test, iterate=True)
        self.assertNotEqual(out, base64.b64encode(test),
            "Input from bytes with iterate not properly iterated")
        self.assertEqual(out, base64.b64encode(test[:5]) + base64.b64encode(test[5:]),
            "Input from bytes with iterate produced inaccurate results")
        
    def test_do_input_bytes_generate(self):
        """
        lets.do should be able to handle bytes as input with generate.
        """
        import lets, base64
        test = b"abcd\nefgh\n"
        out = next(lets.do("encode/base64", input=test, generate=True))
        self.assertNotEqual(out, base64.b64encode(test[:5]),
            "Input from bytes with generate improperly iterated")
        self.assertEqual(out, base64.b64encode(test),
            "Input from bytes with generate produced inaccurate results")
        
    def test_do_input_bytes_iterate_generate(self):
        """
        lets.do should be able to handle bytes as input with iterate and generate.
        """
        import lets, base64
        test = b"abcd\nefgh\n"
        out = next(lets.do("encode/base64", input=test, iterate=True, generate=True))
        self.assertNotEqual(out, base64.b64encode(test),
            "Input from bytes with iterate and generate not properly iterated")
        self.assertEqual(out, base64.b64encode(test[:5]),
            "Input from bytes with iterate and generate produced inaccurate results")
        
    #
    # lets.do input string
    #

    def test_do_input_string(self):
        """
        lets.do should be able to handle a string as input.
        """
        import lets, string, base64
        test = string.printable
        out = lets.do("encode/base64", input=test)
        self.assertEqual(out, base64.b64encode(test.encode()),
            "Input from string produced inaccurate results")

    def test_do_input_string_iterate(self):
        """
        lets.do should be able to handle a string as input with iterate.
        """
        import lets, base64
        test = "abcd\nefgh\n"
        out = lets.do("encode/base64", input=test, iterate=True)
        self.assertNotEqual(out, base64.b64encode(test.encode()),
            "Input from string with iterate not properly iterated")
        self.assertEqual(out, base64.b64encode(test.encode()[:5]) + base64.b64encode(test.encode()[5:]),
            "Input from string with iterate produced inaccurate results")
        
    def test_do_input_string_generate(self):
        """
        lets.do should be able to handle a string as input with generate.
        """
        import lets, base64
        test = "abcd\nefgh\n"
        out = next(lets.do("encode/base64", input=test, generate=True))
        self.assertNotEqual(out, base64.b64encode(test.encode()[:5]),
            "Input from string with generate improperly iterated")
        self.assertEqual(out, base64.b64encode(test.encode()),
            "Input from string with generate produced inaccurate results")
        
    def test_do_input_string_iterate_generate(self):
        """
        lets.do should be able to handle a string as input with iterate and generate.
        """
        import lets, base64
        test = "abcd\nefgh\n"
        out = next(lets.do("encode/base64", input=test, iterate=True, generate=True))
        self.assertNotEqual(out, base64.b64encode(test.encode()),
            "Input from string with iterate and generate not properly iterated")
        self.assertEqual(out, base64.b64encode(test.encode()[:5]),
            "Input from string with iterate and generate produced inaccurate results")
        
    #
    # lets.do input buffer
    #

    def test_do_input_io(self):
        """
        lets.do should be able to handle an io bytes buffer as input.
        """
        import lets, io, base64
        test = bytes(range(0,256))
        with io.BytesIO(test) as b:
            out = lets.do("encode/base64", input=b)
            self.assertEqual(out, base64.b64encode(test),
                "Input from BytesIO produced inaccurate results")

    def test_do_input_io_iterate(self):
        """
        lets.do should be able to handle an io bytes buffer as input with iterate.
        """
        import lets, io, base64
        test = b"abcd\nefgh\n"
        with io.BytesIO(test) as b:
            out = lets.do("encode/base64", input=b, iterate=True)
            self.assertNotEqual(out, base64.b64encode(test),
                "Input from BytesIO with iterate not properly iterated")
            self.assertEqual(out, base64.b64encode(test[:5]) + base64.b64encode(test[5:]),
                "Input from BytesIO with iterate produced inaccurate results")
            
    def test_do_input_io_generate(self):
        """
        lets.do should be able to handle an io bytes buffer as input with generate.
        """
        import lets, io, base64
        test = b"abcd\nefgh\n"
        with io.BytesIO(test) as b:
            out = next(lets.do("encode/base64", input=b, generate=True))
            self.assertNotEqual(out, base64.b64encode(test[:5]),
                "Input from BytesIO with generate improperly iterated")
            self.assertEqual(out, base64.b64encode(test),
                "Input from BytesIO with generate produced inaccurate results")
            
    def test_do_input_io_iterate_generate(self):
        """
        lets.do should be able to handle an io bytes buffer as input with iterate and generate.
        """
        import lets, io, base64
        test = b"abcd\nefgh\n"
        with io.BytesIO(test) as b:
            out = next(lets.do("encode/base64", input=b, iterate=True, generate=True))
            self.assertNotEqual(out, base64.b64encode(test),
                "Input from bytes with iterate and generate not properly iterated")
            self.assertEqual(out, base64.b64encode(test[:5]),
                "Input from BytesIO with generate produced inaccurate results")            

    #
    # lets.do input file
    #

    def test_do_input_file(self):
        """
        lets.do should be able to handle a file object as input.
        """
        import lets, tempfile, base64
        test = bytes(range(0,256))
        with tempfile.NamedTemporaryFile("wb") as w:
            w.write(test)
            w.seek(0)
            with open(w.name, "rb") as r:
                out = lets.do("encode/base64", input=r)
                self.assertEqual(out, base64.b64encode(test),
                    "Input from file produced inaccurate results")

    def test_do_input_file_iterate(self):
        """
        lets.do should be able to handle a file object as input with iterate.
        """
        import lets, tempfile, base64
        test = b"abcd\nefgh\n"
        with tempfile.NamedTemporaryFile("wb") as w:
            w.write(test)
            w.seek(0)
            with open(w.name, "rb") as r:
                out = lets.do("encode/base64", input=r, iterate=True)
                self.assertNotEqual(out, base64.b64encode(test),
                    "Input from bytes with iterate not properly iterated")
                self.assertEqual(out, base64.b64encode(test[:5]) + base64.b64encode(test[5:]),
                    "Input from file with iterate produced inaccurate results")
                
    def test_do_input_file_generate(self):
        """
        lets.do should be able to handle a file object as input with generate.
        """
        import lets, tempfile, base64
        test = b"abcd\nefgh\n"
        with tempfile.NamedTemporaryFile("wb") as w:
            w.write(test)
            w.seek(0)
            with open(w.name, "rb") as r:
                out = next(lets.do("encode/base64", input=r, generate=True))
                self.assertNotEqual(out, base64.b64encode(test[:5]),
                    "Input from file with generate improperly iterated")
                self.assertEqual(out, base64.b64encode(test),
                    "Input from file with generate produced inaccurate results")
                
    def test_do_input_file_iterate_generate(self):
        """
        lets.do should be able to handle a file object as input with iterate and generate.
        """
        import lets, tempfile, base64
        test = b"abcd\nefgh\n"
        with tempfile.NamedTemporaryFile("wb") as w:
            w.write(test)
            w.seek(0)
            with open(w.name, "rb") as r:
                out = next(lets.do("encode/base64", input=r, iterate=True, generate=True))
                self.assertNotEqual(out, base64.b64encode(test),
                    "Input from file with iterate and generate not properly iterated")
                self.assertEqual(out, base64.b64encode(test[:5]),
                    "Input from file with iterate and generate produced inaccurate results")

    #
    # lets.do input list
    #

    def test_do_input_bad_list(self):
        """
        lets.do input list must consist of bytes.
        """
        import lets
        test = ["abcd", "efgh"]
        with self.assertRaises(TypeError):
            out = lets.do("encode/base64", input=test)

    def test_do_input_list(self):
        """
        lets.do should be able to handle a list of bytes as input.
        """
        import lets, base64
        test = [b"abcd", b"efgh"]
        out = lets.do("encode/base64", input=test)
        self.assertEqual(out, base64.b64encode(b"".join(test)),
            "Input from list of bytes produced inaccurate results")

    def test_do_input_list_iterate(self):
        """
        lets.do should be able to handle a list of bytes as input with iterate.
        """
        import lets, base64
        test = [b"abcd", b"efgh"]
        out = lets.do("encode/base64", input=test, iterate=True)
        self.assertNotEqual(out, base64.b64encode(b"".join(test)),
            "Input from list of bytes with iterate not properly iterated")
        self.assertEqual(out, base64.b64encode(test[0]) + base64.b64encode(test[1]),
            "Input from list of bytes with iterate produced inaccurate results")

    def test_do_input_list_generate(self):
        """
        lets.do should be able to handle a list of bytes as input with generate.
        """
        import lets, base64
        test = [b"abcd", b"efgh"]
        out = next(lets.do("encode/base64", input=test, generate=True))
        self.assertNotEqual(out, base64.b64encode(test[0]),
            "Input from list of bytes with generate improperly iterated")
        self.assertEqual(out, base64.b64encode(b"".join(test)),
            "Input from list of bytes with generate produced inaccurate results")

    def test_do_input_list_iterate_generate(self):
        """
        lets.do should be able to handle a list of bytes as input with iterate and generate.
        """
        import lets, base64
        test = [b"abcd", b"efgh"]
        out = next(lets.do("encode/base64", input=test, iterate=True, generate=True))
        self.assertNotEqual(out, base64.b64encode(b"".join(test)),
            "Input from list of bytes with iterate and generate not properly iterated")
        self.assertEqual(out, base64.b64encode(test[0]),
            "Input from list of bytes with iterate and generate produced inaccurate results")

    #
    # lets.do input generator
    #

    def test_do_input_bad_generator(self):
        """
        lets.do input generator must consist of bytes.
        """
        import lets
        test = ["abcd", "efgh"]
        gen = (i for i in test)
        with self.assertRaises(TypeError):
            out = lets.do("encode/base64", input=gen)

    def test_do_input_generator(self):
        """
        lets.do should be able to handle a generator of bytes as input.
        """
        import lets, base64
        test = [b"abcd", b"efgh"]
        gen = (i for i in test)
        out = lets.do("encode/base64", input=gen)
        self.assertEqual(out, base64.b64encode(b"".join(test)),
            "Input from generator of bytes produced inaccurate results")

    def test_do_input_generator_iterate(self):
        """
        lets.do should be able to handle a generator of bytes as input with iterate.
        """
        import lets, base64
        test = [b"abcd", b"efgh"]
        gen = (i for i in test)
        out = lets.do("encode/base64", input=gen, iterate=True)
        self.assertNotEqual(out, base64.b64encode(b"".join(test)),
            "Input from generator of bytes with iterate not properly iterated")
        self.assertEqual(out, base64.b64encode(test[0]) + base64.b64encode(test[1]),
            "Input from generator of bytes with iterate produced inaccurate results")

    def test_do_input_generator_generate(self):
        """
        lets.do should be able to handle a generator of bytes as input with generate.
        """
        import lets, base64
        test = [b"abcd", b"efgh"]
        gen = (i for i in test)
        out = next(lets.do("encode/base64", input=gen, generate=True))
        self.assertNotEqual(out, base64.b64encode(test[0]),
            "Input from generator of bytes with generate improperly iterated")
        self.assertEqual(out, base64.b64encode(b"".join(test)),
            "Input from generator of bytes with generate produced inaccurate results")

    def test_do_input_generator_iterate_generate(self):
        """
        lets.do should be able to handle a generator of bytes as input with iterate and generate.
        """
        import lets, base64
        test = [b"abcd", b"efgh"]
        gen = (i for i in test)
        out = next(lets.do("encode/base64", input=gen, iterate=True, generate=True))
        self.assertNotEqual(out, base64.b64encode(b"".join(test)),
            "Input from generator of bytes with iterate and generate not properly iterated")
        self.assertEqual(out, base64.b64encode(test[0]),
            "Input from generator of bytes with iterate and generate produced inaccurate results")


    #
    # lets.do output file
    #

    def test_do_output_file(self):
        """
        lets.do should ignore 'output', as everything is either
        returned or yielded.
        """
        import lets, tempfile
        test = bytes(range(0,256))
        with self.assertRaises(KeyError):
            with tempfile.NamedTemporaryFile("wb") as f:
                lets.do("encode/base64", test, output=f)

# Included to automatically discover tests
def load_tests(loader, tests, pattern):
    """
    Produce a suite of all tests present in the framework.

    :param unittest.loader.TestLoader loader:
    :param unittest.suite.TestSuite tests:
    :param str pattern:
    """
    suite = unittest.TestSuite()
    handler.setLevel(logging.CRITICAL)

    # Add local tests
    suite.addTests(loader.loadTestsFromTestCase(BashInterfaceTests))
    suite.addTests(loader.loadTestsFromTestCase(PythonInterfaceTests))

    # Add package tests
    from . import module
    suite.addTests(loader.loadTestsFromModule(module))
    from . import logger
    suite.addTests(loader.loadTestsFromModule(logger))
    from . import parser
    suite.addTests(loader.loadTestsFromModule(parser))

    # Add extension tests
    from . import extensions
    for e in extensions.__all__:
        m = __import__(".".join(["lets.extensions", e]))
        suite.addTests(loader.loadTestsFromName(e, extensions))

    # Add module tests
    for mod in load_all():
        tests = loader.loadTestsFromModule(mod)
        suite.addTests(tests)

    return suite

# Handle running from python
def test(module=None):
    """
    Load and run tests present in the framework.

    :param str module: Path of the module to test
    :raises ModuleNotFoundError: If provided module is not found
    :raises TypeError: If provided module is invalid
    """
    if module:
        # Load the module
        mod = load(module)
        if not mod:
            raise ModuleNotFoundError("No module at path: %s" % module)

        # Perform tests found in the module
        unittest.main(module=mod.__name__)
    else:
        # Perform tests in all modules (automatically discovered)
        unittest.main(module=__package__)
