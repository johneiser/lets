#!/usr/bin/env python3
import os, sys, unittest
from lets.module import Module

if __name__ == "__main__":

    # Initialize test suite
    suite = unittest.TestSuite()

    # Walk modules and add tests
    for mod in Module.build_all():
        if mod and hasattr(mod, Module.test_method):
            suite.addTest(mod)

    # Execute test suite
    runner = unittest.TextTestRunner()
    runner.run(suite)