#!/bin/bash

echo -n "abcd" \
    | lets encode/base64 -v \
    | lets decode/base64 -v
# [+] |Base64| Running module with 4 bytes and options: {'verbose': True}
# [+] |Base64| Running module with 8 bytes and options: {'verbose': True}
# abcd