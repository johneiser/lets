"""

Once :doc:`installed <install>`, :code:`lets` becomes available as a
command in the bash terminal.

.. code-block:: bash

    $ lets -h
    usage: lets [-h] [-v] [-i] [-g] module ...

    positional arguments:
    module          module to use
    options         options to provide to the module

    optional arguments:
    -h, --help      show this help message and exit
    -v, --verbose   show extra information
    -i, --iterate   iterate input over newlines
    -g, --generate  generate output with newlines

With :doc:`bash tab-completion <install>` configured, :code:`[TAB]` can be used
to browse available modules.

.. code-block:: bash

    $ lets sample/my[TAB][TAB]
    sample/mydockermodule   sample/mymodule

Each module provides its own help text.

.. code-block:: bash

    $ lets encode/base64 -h
    usage: base64 [-h] [-v] [-i] [-g]

    Base64 encode a string of bytes.

    optional arguments:
    -h, --help      show this help message and exit
    -v, --verbose   show extra information
    -i, --iterate   iterate input over newlines
    -g, --generate  generate output with newlines

Visit the `Module Explorer <https://johneiser.github.io/lets/>`_ to browse
what modules are available.

By default, when invoking a module from the bash interface, input is
pulled from *stdin*. This enables the two most common ways of passing
data into a module, as shown below:

.. code-block:: bash

    $ echo 'input' | lets encode/base64     # Input bytes
    aW5wdXQK

    $ lets encode/base64 <file.txt          # Input file
    aW5wdXQK

:code:`iterate` and :code:`generate` provide subtle adjustments to the way a
module handles input and output data. :code:`iterate` will cause the module
to perform its functionality for each line as opposed to all at once, and
:code:`generate` will cause the module to generate any output as it becomes
available, adding a newline if necessary. The following example demonstrates
this:

.. code-block:: bash

    $ # Process all input, return all output
    $ echo -ne "abcd\\nefgh\\n" | lets encode/base64
    YWJjZAplZmdoCg==$

    $ # Process all input, generate each output
    $ echo -ne "abcd\\nefgh\\n" | lets encode/base64 -g
    YWJjZAplZmdoCg==
    $

    $ # Process each input, generate each output
    $ echo -ne "abcd\\nefgh\\n" | lets encode/base64 -ig
    YWJjZAo=
    ZWZnaAo=

    $ # Process each input, return all output
    $ echo -ne "abcd\\nefgh\\n" | lets encode/base64 -i
    YWJjZAo=ZWZnaAo=

The sum effect is the ability to *chain* modules together in various ways.

.. code-block:: bash

    $ # Convert data from one format to another
    $ echo 'abcd' | lets encode/base64 | lets decode/base64 -g
    abcd

    $ # Filter and react to data
    $ echo "192.168.1.0/24" \\
        | lets scan/network/ping -ig | tee hosts.txt \\
        | lets scan/network/services -ig > services.txt

    $ # Configure and run services
    $ lets generate/config/ftp -u admin -p admin \\
        | lets listen/serve/ftp -p 2021
    [+] Listening ...

"""
import os, sys, argparse, logging
sys.dont_write_bytecode = "LETS_NOCACHE" in os.environ
from .module import load, Module
from .logger import log, handler, LEVEL_DEV
from .parser import CustomArgumentParser, main_parser, module_parser, DEFAULT_ITERATE, DEFAULT_GENERATE

# TODO: lets.list?
# TODO: lets.exists?

def help(module=None):
    """
    Produce a help statement for the specified module.

    :param str module: Path of the module
    :return: Formatted help string
    :rtype: str
    :raises ModuleNotFoundError: If provided module is not found
    :raises TypeError: If provided module is invalid
    """
    if module is not None:
        # Load and find module class (raises ModuleNotFoundError, TypeError)
        cls = Module._find(load(module))

        # Build module parser from module class
        parser, group = module_parser(cls)
        cls.add_arguments(group)

    else:
        # Build main parser
        parser = main_parser()

    # Return formatted help
    return parser.format_help()

def usage(module=None):
    """
    Produce a usage statement for the specified module.

    :param str module: Path of the module
    :return: Formatted help string
    :rtype: str
    :raises ModuleNotFoundError: If provided module is not found
    :raises TypeError: If provided module is invalid
    """
    if module is not None:
        # Load and find module (raises ModuleNotFoundError, TypeError)
        cls = Module._find(load(module))

        # Build module parser from module
        parser, group = module_parser(cls)
        cls.add_arguments(group)

    else:
        # Build main parser
        parser = main_parser()

    # Return formatted help
    return parser.format_usage()

# Handle running from python
def do(module, input=None, iterate=DEFAULT_ITERATE, generate=DEFAULT_GENERATE, **kwargs):
    """
    Build and execute a module with the specified data and options.

    :param str module: Path of the module to use
    :param input: Input to provide to the module
    :type input: bytes, str, list, generator or file-like object
    :param bool iterate: Whether to iterate input over newlines
    :param bool generate: Whether to generate output
    :param ** kwargs: Options for the module
    :return: Output from the module
    :rtype: generator or bytes
    :raises ModuleNotFoundError: If provided module is not found
    :raises TypeError: If provided module is invalid
    :raises KeyError: If provided key is invalid
    :raises ValueError: If provided value is invalid
   
    From within the python interface, :code:`input` can take many forms:

    .. code-block:: python

        import lets

        # String
        lets.do("encode/base64", "string")

        # Bytes
        lets.do("encode/base64", b"bytes")

        # List
        l = [b"list"]
        lets.do("encode/base64", l, iterate=True)

        # Generator
        g = (i for i in l)
        lets.do("encode/base64", g, iterate=True)

        # Buffer
        from io import BytesIO
        with BytesIO(b"buffer") as b:
            lets.do("encode/base64", b)

        # File or file-like object
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile() as f:
            f.write(b"file")
            f.seek(0)
            lets.do("encode/base64", f)

    :code:`iterate` and :code:`generate` provide subtle adjustments to
    the way input and output are handled. :code:`iterate` will cause the
    module to perform its functionality for each line in data (or each
    item in list) provided as input, and :code:`generate` will cause the
    module to generate any output as it becomes available. The following
    example demonstrates this:

    .. code-block:: python

        >> import lets
        >> test = [b"abcd", b"efgh"]

        >> # Process all input, return all output
        >> lets.do("encode/base64", test)
        b'YWJjZGVmZ2g='

        >> # Process all input, generate each output
        >> list(lets.do("encode/base64", test,
                generate=True))
        [b'YWJjZGVmZ2g=']

        >> # Process each input, generate each output
        >> list(lets.do("encode/base64", test,
                iterate=True, generate=True))
        [b'YWJjZA==', b'ZWZnaA==']

        >> # Process each input, return all output
        >> lets.do("encode/base64", test,
                iterate=True)
        b'YWJjZA==ZWZnaA=='

    """
    last_level = handler.level
    try:
        # Load and find module (raises ModuleNotFoundError, TypeError)
        cls = Module._find(load(module))

        # Increase verbosity if necessary
        if "LETS_DEBUG" in os.environ:
            handler.setLevel(LEVEL_DEV)
        elif kwargs.get("verbose") and handler.level > logging.DEBUG:
            handler.setLevel(logging.DEBUG)

        # Build module argument parser
        parser, group = module_parser(cls)
        cls.add_arguments(group)

        # Add main kwargs to dictionary
        kwargs["input"] = input
        if iterate is not DEFAULT_ITERATE:
            kwargs["iterate"] = True    # Only include if specified! (action='store_true')
        if generate is not DEFAULT_GENERATE:
            kwargs["generate"] = True   # Only include if specified! (action='store_true')

        # Validate kwargs
        if "output" in kwargs:
            # Output is not relevant here, as everything is returned or yielded
            raise KeyError("Invalid argument provided: 'output'")

        # Parse keyword arguments from dictionary (raises ValueError)
        kwargs = parser.parse_kwargs(**kwargs)

        # Instantiate module (raises TypeError)
        module = cls(**kwargs)

        # Execute module
        results = module.do(**kwargs)

        # Produce results accordingly
        return results if module._generate else b"".join(results)

    finally:
        # Restore logging level
        handler.setLevel(last_level)

# Handle running from bash (module)
def _main(cls, options, **kwargs):
    """
    Parse arguments from the remainder options and pass them to the module.

    :param cls type: Successfully identified module class
    :param options list: Remainder options passed through the terminal
    :param **kwargs: Defaults already parsed from the main parser
    :raises module.Exception: If module raises an Exception
    :raises TypeError: If provided argument is invalid
    :raises ValueError: If provided argument value is invalid
    """
    # Parse arguments from the remainder of options
    parser, group = module_parser(cls, **kwargs)
    cls.add_arguments(group)
    args = parser.parse_args(options)
    kwargs = vars(args)

    # Increase verbosity if necessary
    if args.verbose and handler.level > logging.DEBUG:
        handler.setLevel(logging.DEBUG)

    # Restore system stdin to tty
    if not sys.stdin.isatty():
        sys.stdin = open("/dev/tty")

    # Redirect any extra standard output to stderr
    sys.stdout = sys.stderr

    # Instantiate module (raises TypeError)
    module = cls(args.input, args.output, args.iterate, args.generate)

    try:
        # Execute module
        results = module.do(**kwargs)

        # Produce results accordingly
        if results:
            for result in results:
                if result:
                    if module._generate and not result.endswith(b"\n"):
                        result += b"\n"
                    module._output.write(result)
                    module._output.flush()
    
    # Handle broken pipes within module
    except BrokenPipeError as e:
        try:
            module._output.close()
        except BrokenPipeError as e:
            raise
    
    # Wrap exceptions with their module's name
    # except Exception as e:
    #     log.exception("Exception raised in %s", cls.__name__)
    #     raise module.Exception from e

# Handle running from bash (global)
def main():
    """
    Parse arguments from the terminal and perform the appropriate action.
    """
    # Parse arguments from the terminal
    parser = main_parser()
    args = parser.parse_args()
    kwargs = vars(args)    

    # Show development level logs (bash only)
    if args.verbose or "LETS_DEBUG" in os.environ:
        handler.setLevel(LEVEL_DEV)

    try:
        # Load and find module class (raises TypeError, ModuleNotFoundError)
        module = kwargs.pop("module")
        cls = Module._find(load(module))

        # Continue with module
        _main(cls, **kwargs)

    # Handle failure to find module
    except ModuleNotFoundError as e:
        log.critical(e)

    # Handle bad argument syntax
    except (TypeError, ValueError) as e:
        log.critical(e)

    # Handle all exceptions inside module
    # except Module.Exception as e:
    #     log.error("%s: %s",
    #         e.__class__.__name__,
    #         e.__cause__ or str(e))

    except Exception as e:
        log.exception(e)

    # Handle early cancellation by user
    except KeyboardInterrupt:
        sys.stderr.buffer.write(b"\n")
        sys.stderr.buffer.flush()

    finally:
        # Restore logging level
        handler.setLevel(logging.INFO)

# Handle running the file directly
if __name__ == "__main__":
    main()
