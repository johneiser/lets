#!/bin/bash

# Find lets
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"

# Use lets
echo -n "abcd" \
    | "$DIR/lets.py" encode/base64 -v \
    | "$DIR/lets.py" decode/base64 -v
# [+] |Base64| Running module with 4 bytes and options: {'verbose': True}
# [+] |Base64| Running module with 8 bytes and options: {'verbose': True}
# abcd