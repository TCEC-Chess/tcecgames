#!/usr/bin/python3

import chess.pgn
import sys


def compactify_game(game, num):
    # strip root comment
    game.comment = None
    last_book_node = game
    non_book_node_found = False

    # check that we have the "Site" header
    if not "Site" in game.headers:
        print(f"Error in game {num}: Missing tag 'Site'", file=sys.stderr)
        sys.exit(2)

    # note: we start from the root node which is one before the first move
    node = game
    while True:

        # next mainline move
        if (len(node.variations) > 0):
            # strip every other variation except the mainline
            #node.variations = node.variations[0:1]
            node = node.variations[0]
        else:
            node = None
            break

        # check if this is a book node
        if not non_book_node_found:

            comment = node.comment
            if comment is None:
                comment = ""

            # the very old style (seasons 1..5)
            if comment.startswith("ev=0.00, d=1, mt=00:00:00"):
                last_book_node = node
            elif comment == "book" or comment.startswith("book, "): # the modern
                last_book_node = node
            else:
                non_book_node_found = True

        node.comment = None

    # mark the last book node
    last_book_node.comment = "Book exit"

    print(game)
    print("")

    if len(game.errors) > 0:
        print(f"Error in game {num}. Exiting!", file=sys.stderr)
        sys.exit(2)

def main(argv):
    # version check -- this script was developed with Python 3.9
    if sys.version_info < (3, 9):
        warning(f"Python version {sys.version_info.major}.{sys.version_info.minor} is not at least 3.9!")

    inputfile = argv[0]
    num = 0

    with open(inputfile, "r") as f:
        while True:
            num = num + 1
            game = chess.pgn.read_game(f)
            if game is None:
                break

            compactify_game(game, num)
