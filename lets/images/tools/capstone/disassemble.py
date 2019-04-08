#!/usr/bin/env python
import os, sys, argparse, binascii, pprint
import capstone

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=str, help="file containing bytes to disassemble")
    parser.add_argument("arch", type=str, help="architecture to use")
    parser.add_argument("mode", type=str, help="mode to use")
    parser.add_argument("outfile", type=str, help="file to write disassembled code")
    args = parser.parse_args()

    try:
        arch = getattr(capstone, "CS_ARCH_%s" % args.arch)
        mode = getattr(capstone, "CS_MODE_%s" % args.mode)
        cs = capstone.Cs(arch, mode)
        with open(args.infile, "rb") as fin:
            with open(args.outfile, "w") as fout:
                for i in cs.disasm(fin.read(), 0):
                    fout.write("0x{:<4}   {:<20}   {:<8} {:<12}\n".format(
                            i.address,
                            binascii.hexlify(i.bytes).decode(),
                            i.mnemonic,
                            i.op_str))
    except KeyError as e:
        raise(Exception("Architecture %s not supported" % str(e)))
    # except AttributeError as e:
    #     raise(e)