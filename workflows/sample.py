#!/usr/bin/env python3

import lets

encoded = lets.do("encode/base64",
    b"abcd", {"verbose" : True})
# [+] |Base64| Running module with 4 bytes and options: {'verbose': True}

decoded = lets.do("decode/base64",
    encoded, {"verbose" : True})
# [+] |Base64| Running module with 8 bytes and options: {'verbose': True}

print(decoded)
# b'abcd'