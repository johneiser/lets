#!/usr/bin/env python
import os, sys, argparse
import keystone

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=str, help="file containing code to assemble")
    parser.add_argument("arch", type=str, help="architecture to use")
    parser.add_argument("mode", type=str, help="mode to use")
    parser.add_argument("outfile", type=str, help="file to write assembled bytes")
    args = parser.parse_args()

    try:
        arch = getattr(keystone, "KS_ARCH_%s" % args.arch)
        mode = getattr(keystone, "KS_MODE_%s" % args.mode)
        ks = keystone.Ks(arch, mode)
        with open(args.infile, "rb") as fin:
            bites, count = ks.asm(fin.read(), as_bytes=True)
            with open(args.outfile, "wb") as fout:
                fout.write(bites)
    except KeyError as e:
        raise(Exception("Architecture %s not supported" % str(e)))
    # except AttributeError as e:
    #     raise(e)