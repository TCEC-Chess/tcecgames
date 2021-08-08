#!/usr/bin/python3

# hack to make python compile the gamelist processor...
import processgamelistjson
import sys

if __name__ == "__main__":
    processgamelistjson.main(sys.argv[1:])

