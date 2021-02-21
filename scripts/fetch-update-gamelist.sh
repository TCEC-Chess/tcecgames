#!/bin/bash

set -e
cd "$(dirname $0)"/..

wget https://tcec-chess.com/gamelist.json --output-document=master-archive/gamelist.json

