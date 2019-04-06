#!/usr/bin/env python3
import os, sys, argparse, logging
from lets.module import Module

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Lets :: A Modular Framework for Arbitrary Action",
        usage="[input] | %(prog)s <module> [options]"
        )
    parser.add_argument("module", metavar="module", type=str, help="module to use")
    parser.add_argument("options", metavar="options", type=str, nargs=argparse.REMAINDER, help="options to provide to the module")
    args = parser.parse_args()

    try:

        # Fetch data from stdin
        data = b""
        if not sys.stdin.isatty():
            data = sys.stdin.buffer.read()

        # Build module
        mod = Module.build(args.module)
        if mod:

            # Execute module
            gen = mod.do(data, mod.parse(args.options))

            if gen:
                # Print results
                for i in gen:
                    sys.stdout.buffer.write(i)
                    sys.stdout.buffer.flush()

        else:
            raise(Module.Exception("Error loading module: %s" % args.module))

    except KeyboardInterrupt:
        pass

    except Module.Exception as e:
        logging.error("[!] %s" % (str(e)))