#!/usr/bin/python3

# hack to make python compile the compactifier...
import compactifypgn
import sys

if __name__ == "__main__":
    compactifypgn.main(sys.argv[1:])
