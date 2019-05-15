#!/bin/bash

# Use remote lets api
echo -n "abcd" \
    | curl -sd@- "localhost:8080/lets/encode/base64" \
    | curl -sd@- "localhost:8080/lets/decode/base64"
# abcd