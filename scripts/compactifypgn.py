#!/usr/bin/python3

import chess.pgn
import sys


def compactify_game(game, num):
    # strip root comment
    game.comment = None
    last_book_node = game
    non_book_node_found = False
    thoresen2 = False
    force_book_exit_ply = None

    # check that we have the "Site" header
    if not "Site" in game.headers:
        print(f"Error in game {num}: Missing tag 'Site'", file=sys.stderr)
        sys.exit(2)

    if game.headers["Site"].startswith('https://tcec-chess.com/#season=0&div=thort2&'):
        thoresen2 = True
    if game.headers["Site"].startswith('https://tcec-chess.com/#season=0&div=thorm1&'):
        thoresen2 = True
    if game.headers["Site"].startswith('https://tcec-chess.com/#season=0&div=thorm2&'):
        thoresen2 = True
    if game.headers["Site"].startswith('https://tcec-chess.com/#season=0&div=thorm3&'):
        thoresen2 = True
    if game.headers["Site"] == "https://tcec-chess.com/#season=0&div=thort1&game=29":
        thoresen2 = True
        force_book_exit_ply = 16 # best guess

    # note: we start from the root node which is one before the first move
    node = game
    ply = 0
    while True:
        # next mainline move
        if (len(node.variations) > 0):
            # strip every other variation except the mainline
            node = node.variations[0]
        else:
            node = None
            break

        ply = ply + 1

        # check if this is a book node
        if not non_book_node_found:
            comment = node.comment
            if comment is None:
                comment = ""

            if not thoresen2:
                # the ancient style (Thoresen tournament 1)
                if comment == "B 0" or comment == "0 B/ 0":
                    last_book_node = node
                # thoresen specials
                elif comment == "ev=0,d=1,tl=02:00:00" or comment == "Eval = 0, Depth = 1, TimeLeft = 02:00:00" or \
                     comment == "Eval = 0.00, Depth = 1, TimeLeft = 02:00:00" or comment == "ev=0.00,d=1,tl=02:00:00":
                    last_book_node = node
                elif comment.startswith("Eval = 0.00, Depth = 1, MoveTime = 00:00:00"):
                    print(f"Thoresen special", file=sys.stderr)
                    last_book_node = node
                    # the very old style (seasons 1..5)
                elif comment.startswith("ev=0.00, d=1, mt=00:00:00"):
                    last_book_node = node
                elif comment == "book" or comment.startswith("book, "): # the modern
                    last_book_node = node
                else:
                    non_book_node_found = True
            else:
                # thoresen tournament 2 style, also used in match 1-3
                if force_book_exit_ply is None:
                    if comment == "":
                        last_book_node = node
                    else:
                        non_book_node_found = True
                else:
                    if force_book_exit_ply == ply:
                        last_book_node = node

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
