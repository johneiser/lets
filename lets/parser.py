"""

Define a custom argument parser that can expand the usefulness of 
argparse to multiple interfaces.

"""
import os, sys, argparse, pprint
from unittest import TestCase
from .logger import log, LEVEL_DEV

DEFAULT_VERBOSE     = False
DEFAULT_INPUT       = sys.stdin.buffer
DEFAULT_OUTPUT      = sys.stdout.buffer
DEFAULT_ITERATE     = False
DEFAULT_GENERATE    = False

class CustomArgumentParser(argparse.ArgumentParser):
    """
    A custom wrapper around the ArgumentParser is used to add
    additional functionality and improve convenience for modules.

    For example, using this parser, a module can suppress certain
    global arguments from showing up in the help menu. This can help
    limit confusion when global arguments are no longer relevant
    during the module's execution. Note this does not eliminate the
    arguments entirely to be replaced, as many of these global
    arguments are required outside of the module's execution.

    .. code-block:: python

        @classmethod
        def add_arguments(self, parser):
            parser.suppress_argument("iterate")

    """

    def suppress_argument(self, dest):
        """
        Suppress the specified argument destination name from the
        help menu.

        :param str dest: Argument destination name to suppress
        """
        for action in self._actions:
            if action.dest and action.dest == dest:
                action.help = argparse.SUPPRESS

    def parse_kwargs(self, **kwargs):
        """
        Parse input from a number of keyword arguments.

        :param ** kwargs: Keyword arguments to parse
        :return: Parsed keyword arguments
        :rtype: dict
        :raises ValueError: If provided argument is invalid
        """
        log.log(LEVEL_DEV, "Arguments provided:\n%s", pprint.pformat(kwargs))
        try:
            namespace = argparse.Namespace()
            for action in self._actions:
                if action.dest:

                    # Validate specified arguments
                    if action.dest in kwargs:
                        value = kwargs.get(action.dest)

                        # Validate type (raises TypeError)
                        # NOTE: Replaces self._get_value(action, value)
                        if action.type in (str, int, float, bool):
                            value = action.type(value)

                        self._check_value(action, value)    # Check choices
                        action(self, namespace, value)      # Take action (store, store_true, etc..)

                    # Default missing arguments
                    else:
                        value = action.default
                        self._check_value(action, value)    # Check choices
                        kwargs[action.dest] = value

            kwargs.update(vars(namespace))
            log.log(LEVEL_DEV, "Arguments parsed:\n%s", pprint.pformat(kwargs))
            return kwargs

        except argparse.ArgumentError as e:
            raise ValueError(e) from e

def main_parser(verbose=DEFAULT_VERBOSE, input=DEFAULT_INPUT, output=DEFAULT_OUTPUT, iterate=DEFAULT_ITERATE, generate=DEFAULT_GENERATE, **kwargs):
    """
    Primary argument parser with general usage and global arguments.

    :return: Argument parser
    :rtype: :py:class:`argparse.ArgumentParser`
    :meta private:
    """
    parser = CustomArgumentParser(
        description="== Lets :: A Modular Framework for Arbitrary Action ==",
        prog=__package__,
        epilog="tab-completion (bash):\n  lets complete/bash >> ~/.profile && source ~/.profile\n ",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", action="store_true", help="show extra information", default=False)
    parser.add_argument(      "--input", type=argparse.FileType("rb"), help=argparse.SUPPRESS, default=sys.stdin.buffer)
    parser.add_argument("-o", "--output", type=argparse.FileType("wb"), help=argparse.SUPPRESS, default=sys.stdout.buffer)
    parser.add_argument("-i", "--iterate", action="store_true", help="iterate input over newlines", default=False)
    parser.add_argument("-g", "--generate", action="store_true", help="generate output with newlines", default=False)
    parser.add_argument("module", type=str, help="module to use")
    parser.add_argument("options", type=str, nargs=argparse.REMAINDER, help="options to provide to the module")
    return parser

def module_parser(cls, verbose=DEFAULT_VERBOSE, input=DEFAULT_INPUT, output=DEFAULT_OUTPUT, iterate=DEFAULT_ITERATE, generate=DEFAULT_GENERATE, **kwargs):
    """
    Module argument parser with added module-specific arguments.

    :return: ArgumentParser and ArgumentGroup
    :rtype: tuple(:py:class:`argparse.ArgumentParser`, :py:class:`argparse._ArgumentGroup`)
    :meta private:
    """
    parser = CustomArgumentParser(
        prog=cls.__name__.lower(),
        description=cls.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", action="store_true", help="show extra information", default=verbose)
    parser.add_argument(      "--input", type=argparse.FileType("rb"), help=argparse.SUPPRESS, default=input)
    parser.add_argument("-o", "--output", type=argparse.FileType("wb"), help=argparse.SUPPRESS, default=output)
    parser.add_argument("-i", "--iterate", action="store_true", help="iterate input over newlines", default=iterate)
    parser.add_argument("-g", "--generate", action="store_true", help="generate output with newlines", default=generate)

    # Add module arguments to its own group
    group = parser.add_argument_group("module arguments")

    # Apply CustomArgumentParser attributes to the group object
    setattr(group, "suppress_argument", parser.suppress_argument)
    setattr(group, "parse_kwargs", parser.parse_kwargs)

    return parser, group

class ParserTests(TestCase):
    """
    Ensure parser works as expected.

    :meta private:
    """
    parser = None

    default_string = "test"
    default_int = 42
    default_float = 3.14
    default_flag = False
    default_file = sys.stdout.buffer

    def setUp(self):
        self.parser = CustomArgumentParser()
        self.parser.add_argument("string", type=str, default=self.default_string)
        self.parser.add_argument("int", type=int, default=self.default_int)
        self.parser.add_argument("float", type=float, default=self.default_float)
        self.parser.add_argument("-f", "--flag", action="store_true", default=self.default_flag)
        self.parser.add_argument("--file", type=argparse.FileType("wb"), default=self.default_file)

    #
    # string
    #

    def test_parse_kwargs_string_empty(self):
        """
        Default string should automatically populate.
        """
        kwargs = self.parser.parse_kwargs()
        self.assertTrue("string" in kwargs, "Default string missing from parsed kwargs")
        self.assertEqual(kwargs["string"], self.default_string, "Default string incorrectly populated")

    def test_parse_kwargs_string(self):
        """
        String argument should match supplied string.
        """
        test = "abcd"
        kwargs = self.parser.parse_kwargs(string=test)
        self.assertTrue("string" in kwargs, "Supplied string missing from parsed kwargs")
        self.assertEqual(kwargs["string"], test, "String argument does not match supplied string")

    def test_parse_kwargs_string_cast(self):
        """
        Value supplied to string should be properly cast to str.
        """
        test = 1
        kwargs = self.parser.parse_kwargs(string=test)
        self.assertTrue("string" in kwargs, "String missing from parsed kwargs")
        self.assertEqual(kwargs["string"], "1", "String argument not properly cast to str")

    def test_help_string(self):
        """
        String argument should show up in help text.
        """
        out = self.parser.format_help()
        self.assertTrue("string" in out, "String argument missing from help text")

    def test_help_string_suppress(self):
        """
        Suppressed string argument should not show up in help text.
        """
        self.parser.suppress_argument("string")
        out = self.parser.format_help()
        self.assertTrue("string" not in out, "Suppressed string argument still present in help text")

    #
    # int
    #

    def test_parse_kwargs_int_empty(self):
        """
        Default int should automatically populate.
        """
        kwargs = self.parser.parse_kwargs()
        self.assertTrue("int" in kwargs, "Default int missing from parsed kwargs")
        self.assertEqual(kwargs["int"], self.default_int, "Default int incorrectly populated")

    def test_parse_kwargs_int(self):
        """
        Int argument should match supplied int.
        """
        test = 9
        kwargs = self.parser.parse_kwargs(int=test)
        self.assertTrue("int" in kwargs, "Supplied int missing from parsed kwargs")
        self.assertEqual(kwargs["int"], test, "Int argument does not match supplied int")

    def test_parse_kwargs_int_cast(self):
        """
        Value supplied to int should be properly cast to int.
        """
        test = "1"
        kwargs = self.parser.parse_kwargs(int=test)
        self.assertTrue("int" in kwargs, "Int missing from parsed kwargs")
        self.assertEqual(kwargs["int"], 1, "Int argument not properly cast to int")

    def test_parse_kwargs_int_bad_cast(self):
        """
        Handle when value supplied to int cannot be cast.
        """
        test = "a"
        with self.assertRaises(ValueError):
            kwargs = self.parser.parse_kwargs(int=test)

    def test_help_int(self):
        """
        Int argument should show up in help text.
        """
        out = self.parser.format_help()
        self.assertTrue("int" in out, "Int argument missing from help text")

    def test_help_int_suppress(self):
        """
        Suppressed int argument should not show up in help text.
        """
        self.parser.suppress_argument("int")
        out = self.parser.format_help()
        self.assertTrue("int" not in out, "Suppressed int argument still present in help text")

    #
    # float
    #

    def test_parse_kwargs_float_empty(self):
        """
        Default float should automatically populate.
        """
        kwargs = self.parser.parse_kwargs()
        self.assertTrue("float" in kwargs, "Default float missing from parsed kwargs")
        self.assertEqual(kwargs["float"], self.default_float, "Default float incorrectly populated")

    def test_parse_kwargs_float(self):
        """
        Float argument should match supplied float.
        """
        test = 9.4
        kwargs = self.parser.parse_kwargs(float=test)
        self.assertTrue("float" in kwargs, "Supplied float missing from parsed kwargs")
        self.assertEqual(kwargs["float"], test, "Float argument does not match supplied float")

    def test_parse_kwargs_float_cast(self):
        """
        Value supplied to float should be properly cast to float.
        """
        test = "1.0"
        kwargs = self.parser.parse_kwargs(float=test)
        self.assertTrue("float" in kwargs, "Float missing from parsed kwargs")
        self.assertEqual(kwargs["float"], 1.0, "Float argument not properly cast to float")

    def test_parse_kwargs_float_bad_cast(self):
        """
        Handle when value supplied to float cannot be cast.
        """
        test = "a"
        with self.assertRaises(ValueError):
            kwargs = self.parser.parse_kwargs(float=test)

    def test_help_float(self):
        """
        Float argument should show up in help text.
        """
        out = self.parser.format_help()
        self.assertTrue("float" in out, "Float argument missing from help text")

    def test_help_float_suppress(self):
        """
        Suppressed float argument should not show up in help text.
        """
        self.parser.suppress_argument("float")
        out = self.parser.format_help()
        self.assertTrue("float" not in out, "Suppressed float argument still present in help text")

    #
    # flag
    #

    def test_parse_kwargs_flag_empty(self):
        """
        Default flag should automatically populate.
        """
        kwargs = self.parser.parse_kwargs()
        self.assertTrue("flag" in kwargs, "Default flag missing from parsed kwargs")
        self.assertEqual(kwargs["flag"], self.default_flag, "Default flag incorrectly populated")

    def test_parse_kwargs_flag(self):
        """
        Flag argument should match the fact that the flag was supplied.
        """
        kwargs = self.parser.parse_kwargs(flag=None)
        self.assertTrue("flag" in kwargs, "Supplied flag missing from parsed kwargs")
        self.assertTrue(kwargs["flag"], "Flag argument does not reflect that flag was supplied")

    def test_help_flag(self):
        """
        Flag argument should show up in help text.
        """
        out = self.parser.format_help()
        self.assertTrue("flag" in out, "Flag argument missing from help text")

    def test_help_flag_suppress(self):
        """
        Suppressed flag argument should not show up in help text.
        """
        self.parser.suppress_argument("flag")
        out = self.parser.format_help()
        self.assertTrue("flag" not in out, "Suppressed flag argument still present in help text")

    #
    # file
    #

    def test_parse_kwargs_file_empty(self):
        """
        Default file should automatically populate.
        """
        kwargs = self.parser.parse_kwargs()
        self.assertTrue("file" in kwargs, "Default file missing from parsed kwargs")
        self.assertEqual(kwargs["file"], self.default_file, "Default file incorrectly populated")

    def test_parse_kwargs_file(self):
        """
        File argument should match supplied file.
        """
        test = sys.stderr.buffer
        kwargs = self.parser.parse_kwargs(file=test)
        self.assertTrue("file" in kwargs, "Supplied file missing from parsed kwargs")
        self.assertEqual(kwargs["file"], test, "File argument does not match supplied file")

    def test_parse_kwargs_file_cast(self):
        """
        File argument should be ignored when casting types.
        """
        test = "abcd"
        kwargs = self.parser.parse_kwargs(file=test)
        self.assertTrue("file" in kwargs, "Supplied file missing from parsed kwargs")
        self.assertEqual(kwargs["file"], test, "File argument corruped by cast")

    def test_help_file(self):
        """
        File argument should show up in help text.
        """
        out = self.parser.format_help()
        self.assertTrue("file" in out, "File argument missing from help text")

    def test_help_file_suppress(self):
        """
        Suppressed file argument should not show up in help text.
        """
        self.parser.suppress_argument("file")
        out = self.parser.format_help()
        self.assertTrue("file" not in out, "Suppressed file argument still present in help text")
