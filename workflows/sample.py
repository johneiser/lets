#!/usr/bin/env python3

# Find lets
import os, sys
sys.path.insert(0, os.path.abspath(os.path.sep.join([os.path.dirname(__file__),".."])))

# Use lets
import lets

encoded = lets.do("encode/base64",
    b"abcd", {"verbose" : True})
# [+] |Base64| Running module with 4 bytes and options: {'verbose': True}

decoded = lets.do("decode/base64",
    encoded, {"verbose" : True})
# [+] |Base64| Running module with 8 bytes and options: {'verbose': True}

print(decoded)
# b'abcd'