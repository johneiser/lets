"""

As a framework, **lets** is composed of a series of modules, each
implementing its own independent functionality.

A module provides functionality to the framework by implementing
a class which inherits the :py:class:`Module <lets.module.Module>`
class and placing that file in the appropriate directory. The class
must have the same name as the file (case-insensitive) in order to be
recognized. Modules are ingested from the following locations (in the
following order):

- Home directory: :code:`~/.lets/modules/`
- Package directory: :code:`<python>/site-packages/lets/modules/`
- Community package directories (if env["LETS_COMMUNITY"] is set):
    :code:`<python>/site-packages/lets_*/modules/`

Within one of these directories, a module is strategically named and
located to represent a brief summary of its functionality.

    :code:`<verb>/[descriptor/]subject/[descriptor/]<module>`

For example, :code:`encode/base64`, :code:`generate/ssl/certificate` and
:code:`format/bash/python` do a good job of describing their functionality
purely by their name and location in the directory structure and will
be easy to find when using the framework.

----------

"""
import os, sys, logging, io, importlib.util, pkgutil, types, tempfile, types
from unittest import TestCase
from .logger import log, handler, LEVEL_DEV

BASE_DIRS = []

# Home directory (~/.lets/)
BASE_DIRS.append(os.path.join(os.path.expanduser("~"), ".lets"))

# Current package directory
BASE_DIRS.append(os.path.dirname(os.path.abspath(__file__)))

# Other package directories (if env["LETS_COMMUNITY"] is set)
if "LETS_COMMUNITY" in os.environ:
    for loader, name, ispkg in pkgutil.iter_modules():
        if ispkg and name.startswith("lets_"):
            path = os.path.join(loader.path, name)
            if path not in BASE_DIRS:
                BASE_DIRS.append(path)

#
# Base module class
#

class Module(object):
    """
    Define an abstract module class which, when implemented, can be
    located and loaded dynamically. Each module must implement the
    :py:meth:`do <lets.module.Module.do>` method and may implement
    the :py:meth:`add_arguments <lets.module.Module.add_arguments>`
    method.
    """

    _input = None
    """
    Actual input buffer - modules use the :py:meth:`get_input` wrapper instead.
    """

    _output = None
    """
    Actual output buffer - modules use :code:`yield` instead.
    """

    _iterate = False
    """
    When a module is invoked, :code:`iterate [-i | --iterate]` may be specified to
    control how the input data should be fed into the module. Normally, the
    module will wait for all data to be received (followed by EOF) before
    processing. If :code:`iterate` is specified, the module will split the input data
    by newline and process each line individually.
    """

    _generate = False
    """
    Normally, when a module produces output data, this data is written
    to the output buffer indiscriminately, assuming that the consumer of that
    data will wait until the end (EOF) before acting on it, if at all. However,
    if *iterate* is specified, it will process each line of data as it comes in.
    To ensure compatibility with a subsequent module that iterates, :code:`generate
    [-g | --generate]` can be specified.
    """

    class Exception(Exception):
        """
        Custom exception class to handle module-specific errors. Any exceptions
        thrown within the module will automatically be wrapped in this named
        exception and logged accordingly.

        :meta private:
        """

    def __init__(self, input=None, output=None, iterate=False, generate=False, **kwargs):
        """
        A module's input and output is configured when instantiated, and can take
        a variety of forms. For example, the bash interface might use a file as
        input, whereas the python interface might use a string or bytes.

        Iteration and generation define how the module should interpret the
        input and output buffers. If :code:`iterate` is specified, the module will
        interpret the input line by line, as opposed to waiting until EOF.
        Similarly, if :code:`generate` is specified, the module will write data
        to the output buffer line by line as it becomes available, as
        opposed to waiting until all the data has been produced.

        :param input: Input stream
        :type input: bytes, str, list, generator or file-like object
        :param output: Output stream
        :type output: :py:class:`io.BufferedWriter` or :py:class:`io.TextIOWrapper`
        :param bool iterate: Whether to iterate input over newlines
        :param bool generate: Whether to generate output
        :raises TypeError: If provided input or output type are not supported
        :meta private:
        """
        # Convert input to iterator
        if input is None:
            self._input = sys.stdin.buffer
        elif isinstance(input, bytes):
            self._input = io.BytesIO(input)
        elif isinstance(input, str):
            self._input = io.BytesIO(input.encode())
        elif isinstance(input, types.GeneratorType):
            self._input = input
        elif isinstance(input, list):
            for i in input:
                if not isinstance(i, bytes):
                    raise TypeError("input: expected bytes instance, %s found " % type(i))
            self._input = iter(input)
        elif isinstance(input, tempfile._TemporaryFileWrapper):
            self._input = iter(input)
        elif isinstance(input, tempfile.SpooledTemporaryFile):
            self._input = iter(input)
        elif isinstance(input, io.BytesIO):
            self._input = input
        elif isinstance(input, io.BufferedReader):  # sys.stdin.buffer, argparse.FileType("rb")
            self._input = input
        elif isinstance(input, io.TextIOWrapper):   # sys.stdin
            self._input = input.buffer
        else:
            raise TypeError("input: expected bytes instance, %s found " % type(input))

        # Determine output
        # NOTE: Output is only used by the bash interface
        if output is None:
            self._output = sys.stdout.buffer
        elif isinstance(output, io.BufferedWriter): # sys.stdout.buffer, argparse.FileType("wb")
            self._output = output
        elif isinstance(output, io.TextIOWrapper):  # sys.stdout
            self._output = output.buffer
        else:
            raise TypeError("output: expected bytes instance, %s found " % type(input))

        # Store additional variables directly
        self._iterate = iterate
        self._generate = generate

        # Customize module exception with name
        self.Exception.__name__ = self.__class__.__name__ + "Exception"

    @classmethod
    def _find(cls, module):
        """
        Find the Module class in the specified python module.

        :param type module: Python module to search
        :return: Module class
        :rtype: :py:class:`lets.module.Module`
        :raises ImportError: If provided module is not found
        :raises TypeError: If provided module is invalid
        :meta private:
        """
        if not isinstance(module, types.ModuleType):
            raise TypeError("_find: expected module instance, %s found " % type(module))

        [_,_,name] = module.__name__.rpartition(".")
        for key in dir(module):
            attr = getattr(module, key)
            if key.lower() == name.lower() and callable(attr) and issubclass(attr, cls) and attr is not cls:
                return attr

        raise ImportError("No module named '%s'" % module)

    #
    # Module overrides
    #

    @classmethod
    def add_arguments(cls, parser):
        """
        Customize an argument parser defining the usage of the module.

        :param parser: ArgumentParser to customize
        :type parser: :py:mod:`ArgumentParser <argparse.ArgumentParser>`
        
        This function can be implemented to add or suppress options available to
        the user:
        
        .. code-block:: python

            @classmethod
            def add_arguments(self, parser):
                parser.suppress_argument("iterate")
                parser.add_argument("-s", "--sleep", type=int,
                            help="seconds to sleep", default=0)
        """

    def do(self, **kwargs):
        """
        Perform the primary functionality of the module. 

        :param ** kwargs: Any arguments specified in :py:meth:`add_arguments <lets.module.Module.add_arguments>`.
        :return: Execution output
        :rtype: generator(bytes)

        If arguments were added in :py:meth:`add_arguments <lets.module.Module.add_arguments>`,
        they can be included in the definition of this function:

        .. code-block:: python

            def do(self, sleep, **kwargs):
                time.sleep(sleep)

        If input data is required, use the :py:meth:`get_input <lets.module.Module.get_input>` generator
        described below:
        
        .. code-block:: python

            if self.has_input():
                for data in self.get_input():
                    handle(data)
        
        If output data is required, simply :code:`yield` it as bytes and it will be
        written to the appropriate output buffer. If information should be
        shown to the user but not delivered to any subsequent modules, use the
        :py:mod:`logger <lets.logger>` to log messages:

        .. code-block:: python

            from lets.logger import log
            yield b"Delivered to output"
            log.info("Always shown to user")
            log.debug("Only shown when 'verbose' is set")        

        """
        raise NotImplementedError()

    #
    # Module utilities
    #

    def has_input(self):
        """
        Utility available to the module which indicates whether
        input data was supplied.

        :return: Whether input data is present
        :rtype: bool

        .. code-block:: python

            if not self.has_input():
                log.error("Input data required")
        """
        return not hasattr(self._input, "isatty") or not self._input.isatty()

    def get_input(self):
        """
        Utility available to the module providing any supplied input
        data.

        :return: Supplied input data, if it exists
        :rtype: generator(bytes)

        .. code-block:: python

            for data in self.get_input():
                handle(data)
        """
        if self._iterate is True:
            for line in self._input:
                yield line
        else:
            yield b"".join(list(iter(self._input)))

#
# Loading modules dynamically
#

def _load(module, base):
    """
    Load the specified module from the specified base directory.

    :param str module: Relative path to module
    :param str base: Directory to search for module
    :return: Loaded module
    :rtype: module
    :raises TypeError: If provied module is invalid
    :raises FileNotFoundError: If provided module is not found within base
    :meta private:
    """
    try:
        if not isinstance(module, str):
            raise TypeError("_load: expected str instance, %s found " % type(module))

        # Module path: <base>/modules[/directories]/<module>.py
        mod_path = os.path.extsep.join([os.path.join(base, "modules", module), "py"])
        log.log(LEVEL_DEV, "Looking for module: %s", mod_path)

        # Module label: lets.modules[.directories...].<module>
        label = os.path.join("lets", "modules", module).replace(os.path.sep, ".")

        # Load module
        spec = importlib.util.spec_from_file_location(label, mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        log.log(LEVEL_DEV, "Found module: %s", mod_path)
        log.log(LEVEL_DEV, "Loading module: %s", label)

        return mod

    except SyntaxError as e:
        # Show stack trace and continue
        log.exception("Bad module: %s", mod_path)

    return None

def load(module):
    """
    Locate and load the specified module.

    :param str module: Relative path to module
    :return: Loaded module
    :rtype: module
    :raises ImportError: If provided module is not found
    :raises TypeError: If provided module is invalid
    :meta private:
    """
    for base in BASE_DIRS:
        try:
            mod = _load(module, base)
            if mod is not None:
                return mod

        except FileNotFoundError as e:
            # Take note and continue
            log.log(LEVEL_DEV, str(e))

    raise ImportError("No module named '%s'" % module)

def load_all():
    """
    Locate and load all modules.

    :return: Generator of loaded modules
    :rtype: generator of modules
    :meta private:
    """
    for base in BASE_DIRS:

        # Walk module directory
        for root, dirs, files in os.walk(os.path.join(base, "modules")):
            for name in files:

                # Identify sub path
                mod_path = os.path.join(root, name)
                [_,_,sub] = mod_path.partition(base + os.path.sep)

                # Identify file type
                [file_path,_,ext] = sub.rpartition(os.path.extsep)
                if ext == "py":

                    try:
                        # Yield label
                        [_,_,module] = file_path.partition(os.path.sep)
                        yield _load(module, base)

                    except FileNotFoundError as e:
                        # Take note and continue (should never get here)
                        log.log(LEVEL_DEV, str(e))

                    except ImportError as e:
                        # Take note and continue
                        log.log(LEVEL_DEV, str(e))

#
# Tests
#

class ModuleTests(TestCase):
    """
    Ensure module loading works as expected.

    :meta private:
    """
    def test_find_no_module(self):
        with self.assertRaises(TypeError):
            m = Module._find(None)

    def test_find_empty(self):
        with self.assertRaises(ImportError):
            m = Module._find(os)

    def test_load_not_found(self):
        with self.assertRaises(ImportError):
            mod = load("")

    def test_load_bad_module(self):
        with self.assertRaises(TypeError):
            mod = load(b"")

    def test_load_no_module(self):
        with self.assertRaises(TypeError):
            mod = load(None)

    def test_load(self):
        module = "encode/base64"
        mod = load(module)
        self.assertIsNotNone(mod, "Failed to load module: %s" % module)
        m = Module._find(mod)
        self.assertIsNotNone(m, "Failed to find module: %s" % module)

    def test_load_all(self):
        gen = load_all()
        self.assertIsNotNone(gen, "Loading all modules returned empty generator")
        for mod in gen:
            self.assertIsNotNone(mod, "Loading all modules included empty module")