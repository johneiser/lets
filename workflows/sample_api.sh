#!/bin/bash

# Define remote endpoint
lets() { curl -sd@- "http://localhost:8080/lets/$1"; }

# Use lets api
echo -n "abcd" \
    | lets "encode/base64?verbose=true" \
    | lets "decode/base64?verbose=true"
# abcd
