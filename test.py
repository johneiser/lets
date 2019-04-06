#!/usr/bin/env python3
import os, sys, argparse, unittest
from lets.module import Module

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
        mod = Module.build(args.module)
        if mod:
            suite.addTest(mod)
        else:
            raise(Module.Exception("Error loading module: %s" % args.module))

    else:
        # Walk modules and add tests
        for mod in Module.build_all():
            if mod and hasattr(mod, Module.test_method):
                suite.addTest(mod)

    # Execute test suite
    runner = unittest.TextTestRunner()
    runner.run(suite)