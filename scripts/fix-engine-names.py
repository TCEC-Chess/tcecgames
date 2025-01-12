#!/usr/bin/python3

import re
import sys

# Exceptional names. Individually mapped to name / version / optional special tag
#
# Special tag is rarely used. Usually, it is for event-specific
# additional information.
exceptionalNames = {
    # format: <player tag> : (<engine name>, <engine version>, <optional special tag>)
    "Koivisto2 4.41": ("Koivisto", "4.41", "2"),
    "MrBob 1.0.0_dev": ("Mr_Bob", "1.0.0_dev"),
    "Stockfish0_1pct 20191225": ("Stockfish0.1pct", "20191225"),
    "Weiss 0.10-dev-20200525 1": ("Weiss", "0.10-dev-20200525", "1"),
    "Weiss 0.10-dev-20200525 2": ("Weiss", "0.10-dev-20200525", "2"),
    "Crafty_25.2_CCRL 64-bit 4CPU": ("Crafty", "25.2", "CCRL 64-bit 4CPU"),
    "Glaurung_2.2_CCRL 64-bit_4CPU": ("Glaurung", "2.2", "CCRL 64-bit 4CPU"),
    "Gull_20170410_CCRL 64-bit 4CPU": ("Gull", "20170410", "CCRL 64-bit 4CPU"),
    "Komodo_10_CCRL 64-bit_4CPU": ("Komodo", "10", "CCRL 64-bit 4CPU"),
    "Komodo_14_CCRL 64-bit_4CPU": ("Komodo", "14", "CCRL 64-bit 4CPU"),
    "Stockfish_11_CCRL 64-bit_4CPU": ("Stockfish", "11", "CCRL 64-bit 4CPU"),
    "Stockfish_13_CCRL 64-bit_4CPU": ("Stockfish", "13", "CCRL 64-bit 4CPU"),
    "Stockfish_15_CCRL 64-bit_4CPU": ("Stockfish", "15", "CCRL 64-bit 4CPU"),
}


def addSwissTestStockfishVersions():
    for i in range(1, 43):
        exceptionalNames[f"{i:02}Stockfish 2021013116"] = (
            "Stockfish",
            "2021013116",
            f"{i:02}",
        )
        exceptionalNames[f"{i:02}StockfishClassical 202007311012"] = (
            "StockfishClassical",
            "202007311012",
            f"{i:02}",
        )


def addSufiTaggedEngines():
    sufiTriplets = [
        ("Houdini", "1.5a", "Sufi 1&2"),
        ("Houdini", "3", "Sufi 4"),
        ("Houdini", "6.03", "Sufi 10"),
        ("Komodo", "8", "Sufi 5"),
        ("Komodo", "9.2", "Sufi 7"),
        ("Komodo", "9.3", "Sufi 8"),
        ("LCZero", "v0.21.1-nT40.T8.610", "Sufi 15"),
        ("Rybka", "4.1", "Sufi 3"),
        ("Stockfish", "180614", "Sufi 12"),
        ("Stockfish", "18102108", "Sufi 13"),
        ("Stockfish", "190203", "Sufi 14"),
        ("Stockfish", "260318", "Sufi 11"),
        ("Stockfish", "6", "Sufi 6"),
        ("Stockfish", "8", "Sufi 9"),
    ]

    for i in sufiTriplets:
        name1 = f"{i[0]} {i[1]} {i[2]}"
        name2 = f"{i[2].replace(' ', '')} {i[0]} {i[1]}"
        exceptionalNames[name1] = i
        exceptionalNames[name2] = i


def serializeNameVersionTriplet(t):
    if len(t) == 1:
        return t[0]
    elif len(t) == 2:
        return f"{t[0]} ({t[1]})"
    else:
        return f"{t[0]} ({t[1]}) [{t[2]}]"


def fixEngineNames():

    playerTagMatcher = re.compile(r'\[(White|Black) "([^"]*)"\]', re.ASCII)

    regularNameVersionMatcher = re.compile(r"(.*) ([^ ]+)", re.ASCII)

    for line in sys.stdin:
        line = line.rstrip()  # let's skip the newline

        playerTagMatch = playerTagMatcher.fullmatch(line)
        if playerTagMatch:
            player = playerTagMatch.group(2)

            if player in exceptionalNames:
                nameVersionTriplet = exceptionalNames[player]

            elif regularNameVersionMatcher.fullmatch(player):
                m = regularNameVersionMatcher.fullmatch(player)
                nameVersionTriplet = (m.group(1), m.group(2))

            else:
                nameVersionTriplet = (player,)

            print(
                f'[{playerTagMatch.group(1)} "{serializeNameVersionTriplet(nameVersionTriplet)}"]'
            )

        else:
            print(line)


def main(argv):
    # version check -- this script was developed with Python 3.9
    if sys.version_info < (3, 9):
        warning(
            f"Python version {sys.version_info.major}.{sys.version_info.minor} is not at least 3.9!"
        )

    addSwissTestStockfishVersions()
    addSufiTaggedEngines()

    fixEngineNames()


if __name__ == "__main__":
    main(sys.argv[1:])
