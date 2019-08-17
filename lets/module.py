from lets.utility import Utility
from lets.logger import Logger
import os, sys, argparse, unittest, importlib.util, pprint, logging


class Module(Logger, unittest.TestCase):
    """
    Abstract module class, from which all modules inherit.  Provides
    various utilities for each module including identification,
    instantiation, and testing.
    """
    test_method = "test"
    interactive = False
    platforms = ["linux", "win32", "cygwin", "darwin"]

    def __init__(self):
        """
        Custom constructor to enable proper inheritance from unittest.TestCase.
        """
        super().__init__(self.test_method)

        # Check if module works on the current platform
        if sys.platform not in self.platforms:
            self.throw(Exception("Module only available for %s" % str(self.platforms)))

        # Establish clean slate for module options
        self.options = {}

    @classmethod
    def identify(cls, path:str) -> str:
        """
        Attempt to locate and load a module.

        :param path: Path to module
        :return: Label describing newly-loaded module
        """

        # Label: lets.modules.<directories...>.<module>
        label = os.path.sep.join(["lets", "modules", path]).replace(os.path.sep, ".")

        # Module path: <abspath>/lets/modules/<directory>/<modules>
        fullpath = "%s.py" % os.path.sep.join(
            [Utility.core_directory(), "modules", path])

        try:
            # Build import spec
            spec = importlib.util.spec_from_file_location(label, fullpath)
            if spec is not None:

                # Create module
                mod = importlib.util.module_from_spec(spec)

                # Execute module
                spec.loader.exec_module(mod)

                # Store module
                sys.modules[label] = mod

                return label
        except Exception as e:
            cls.Exception.throw(e)

    @classmethod
    def identify_all(cls) -> list:
        """
        Identify all modules.

        :return: Generator of each newly instantiated module
        """
        base = os.path.sep.join([Utility.core_directory(), "modules"])

        # Walk module directory
        for root, dirs, files in os.walk(base):
            for name in files:

                # Identify sub path
                path = os.path.sep.join([root, name])
                [_,_,sub] = path.partition(base + os.path.sep)

                # Identify file type
                [file,_,ext] = sub.rpartition(".")
                if ext == "py":

                    # Yield label
                    yield cls.identify(file)

    @classmethod
    def instantiate(cls, label:str) -> object:
        """
        Instantiate a previously loaded module by its label.  Module must
        contain a class with the same name as the file that inherits this
        class.

        :param label: Label specifying the module to instantiate
        :return: Newly instantiated module
        """

        # Retrieve module from storage
        mod = sys.modules.get(label)
        if mod:

            # Search through keys in module
            for key in dir(mod):
                attr = getattr(mod, key)
                try:

                    # Check if any match the name of the file, are
                    # callable, and inherit this class
                    [_,_,name] = label.rpartition(".")
                    if (str(key).lower() == name.lower() and
                        callable(attr) and
                        issubclass(attr, cls)):

                        return attr()

                except Exception as e:
                    cls.Exception.throw(e)

        return None

    @classmethod
    def build(cls, path:str) -> object:
        """
        Identify and instantiate a module.

        :param path: Path to module
        :return: Newly instantiated module
        """

        # Identify by path
        label = cls.identify(path)
        if label:

            # Instantiate by label
            mod = cls.instantiate(label)
            if mod:

                return mod

            else:
                raise(cls.Exception("Error loading module: %s" % label))
        else:
            raise(cls.Exception("Module not found: %s" % path))

        return None

    @classmethod
    def build_all(cls) -> list:
        """
        Identify and instantiate all modules.

        :return: Generator of each newly instantiated module
        """
        for label in cls.identify_all():
            yield Module.instantiate(label)

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = argparse.ArgumentParser(
            description=self.__doc__,
            prog=self.__class__.__name__.lower())

        # Include verbose / quiet logging with every module
        parser.add_argument("-v", "--verbose",
            help="show extra information",
            action="store_true",
            default=False)
        # parser.add_argument("-q", "--quiet",
        #     help="show minimal information",
        #     action="store_true",
        #     default=False)

        return parser

    def parse(self, args:list=None) -> dict:
        """
        Parse a list of arguments into a dict of options.

        :param args: List of args to be parsed
        :return: Dict of options
        """
        return vars(self.usage().parse_args(args))

    def defaults(self) -> dict:
        """
        Discover the default values of all arguments specified in the
        usage argument parser.

        :return: Dict of options
        """
        defaults = {}
        parser = self.usage()

        for action in parser._actions:
            if "SUPPRESS" not in action.dest:
                try:
                    if "SUPPRESS" not in action.default:
                        defaults[action.dest] = action.default
                except TypeError:
                    defaults[action.dest] = action.default

        for dest, default in parser._defaults.items():
            defaults[dest] = default

        return defaults

    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality of a module.  Update self.options with
        defaults and options, execute functionality, and return results.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        # Update self.options with defaults
        self.options.update(self.defaults())

        # Update self.options with configured options
        if options:
            self.options.update(options)

        if self.options.get("verbose"):
            # Adjust logging down to INFO
            self._log_handler.setLevel(logging.INFO)
            self._log_logger.setLevel(logging.INFO)

        # if self.options.get("quiet"):
        #     # Adjust logging up to ERROR
        #     self._log_handler.setLevel(logging.ERROR)
        #     self._log_logger.setLevel(logging.ERROR)

        self.info("Running module with %d bytes and options: %s" % (
            len(data if data else b""), pprint.pformat(self.options)))

        return iter(())

    def setUp(self):
        """
        Make any necessary preparations for test.
        """
        self._log_handler.setLevel(logging.ERROR)
        self._log_logger.setLevel(logging.ERROR)
        pass

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        self.fail("Not implemented")

    def tearDown(self):
        """
        Clean up after tests have run.
        """
        pass
