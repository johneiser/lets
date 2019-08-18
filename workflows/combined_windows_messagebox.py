#!/usr/bin/env python3
"""
Generate a combined x86/x64 Windows messagebox payload.

Usage: python workflows/combined_windows_messagebox.py | xxd
"""
import sys
import lets

# Build x86 payload
x86 = lets.do("generate/payload/msfvenom",
    options = {"verbose" : True, "options" : [
        "-a", "x86",
        "--platform", "windows",
        "-p", "windows/messagebox",
        "-f", "raw"
    ]})

# Build x64 payload
x64 = lets.do("generate/payload/msfvenom",
    options = {"verbose" : True, "options" : [
        "-a", "x64",
        "--platform", "windows",
        "-p", "windows/x64/messagebox",
        "-f", "raw"
    ]})

# Convert to byte strings
payloads = {
    "x86_bytes" : ",".join([hex(_) for _ in x86]),
    "x64_bytes" : ",".join([hex(_) for _ in x64]),
}

# Build combined payload
asm = """
    xor rax, rax        ; (x86) dec eax; xor eax, eax
    .byte 0x40          ; (x86) inc eax; (x64 - useless rex prefix)
    jnz x86             ; (x86) jnz x86
x64:
    .byte %(x64_bytes)s
    ret
x86:
    .byte %(x86_bytes)s
    ret
""" % payloads

# Assemble combined payload
sc = lets.do("assemble/x64", asm.encode(), {"verbose" : True})

# Write out combined payload 
sys.stdout.buffer.write(sc)
