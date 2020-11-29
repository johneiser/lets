import os, sys, argparse, logging, importlib
from .__module__ import Module, iter_module_packages

log = logging.getLogger(__package__)
log.setLevel(logging.DEBUG)


def main():

    # Process arguments
    parser = argparse.ArgumentParser(__package__)
    parser.add_argument("module", type=str, help="module to use")
    parser.add_argument("options", nargs=argparse.REMAINDER, help="module options")
    parser.add_argument("-i", "--iterate", action="store_true", help="iterate over input")
    parser.add_argument("-g", "--generate", action="store_true", help="generate each output")
    parser.add_argument(      "--input", type=argparse.FileType("rb"), help=argparse.SUPPRESS, default=sys.stdin.buffer)
    parser.add_argument("-o", "--output", type=argparse.FileType("wb"), help="output to file", default=sys.stdout.buffer)
    parser.add_argument("-v", "--verbose", action="store_true", help="print debug info")
    args = parser.parse_args()
    kwargs = vars(args)

    # Configure logging
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log.addHandler(handler)

    # Import specified module
    try:
        mod = None
        path = args.module.replace(os.path.sep, os.path.extsep)
        for pkg in iter_module_packages():
            try:
                mod = importlib.import_module(os.path.extsep + path, pkg)
            except ImportError:
                pass

        assert mod is not None, "No module named '%s'" % path
        assert isinstance(mod, Module), "No module named '%s'" % mod.__name__

        # Re-process arguments with module
        parser = argparse.ArgumentParser(kwargs.pop("module"),
                description=mod.__class__.__doc__,
                formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-i", "--iterate", action="store_true", help="iterate over input")
        parser.add_argument("-g", "--generate", action="store_true", help="generate each output")
        parser.add_argument(      "--input", type=argparse.FileType("rb"), help=argparse.SUPPRESS, default=sys.stdin.buffer)
        parser.add_argument("-o", "--output", type=argparse.FileType("wb"), help="output to file", default=sys.stdout.buffer)
        parser.add_argument("-v", "--verbose", action="store_true", help="print debug info")
        mod.add_arguments(parser)
        args = parser.parse_args(kwargs.pop("options"), args)
        kwargs.update(vars(args))

        # Re-configure logging
        handler.setLevel(logging.DEBUG if (kwargs.pop("verbose")) else logging.INFO)

        # Restore stdin to tty
        if not sys.stdin.isatty():
            sys.stdin = open("/dev/tty")

        # Remove input if not provided
        else:
            kwargs["input"] = None

        # Redirect any extra standard output to stderr
        sys.stdout = sys.stderr

        # Output only used for commandline
        output = kwargs.pop("output")

        # Execute module
        results = mod(**kwargs)

        # Deliver results
        if results:
            if args.generate:
                for result in results:
                    output.write(result)
                    if args.generate and mod.delimiter and not result.endswith(mod.delimiter):
                        output.write(mod.delimiter)
                    output.flush()
            else:
                output.write(results)
                output.flush()

    # Handle user cancellation
    except KeyboardInterrupt:
        sys.stdout.write("\r")
        sys.stdout.flush()

    # Handle missing module
    except ImportError as e:
        log.warning(e)

    # Handle known errors
    except (AssertionError, TypeError) as e:
        log.error(e)

    # Handle upstream pipe disconnect
    except BrokenPipeError as e:
        try:
            output.close()
        except BrokenPipeError as e:
            mod.log.error("No output")
    
    # Handle unknown  errors
    except Exception as e:
        log.exception(e)

