#!/usr/bin/python3

import re
import sys
from tabulate import tabulate

# Exceptional names. Individually mapped to name / version / optional special tag
#
# Special tag is rarely used. Usually, it is for event-specific
# additional information.
exceptionalNames = {
    # format: <player tag> : (<engine name>, <engine version>, <optional special tag>)
    "Antifish 1.0 Mark 289": ("Antifish", "1.0 Mark 289", ""),
    "Bluefish Dev": ("Stockfish", "Dev", "Bluefish"),
    "Booot2 6.5": ("Booot", "6.5", "2"),
    "Chat": ("TCEC Chat", "", ""),
    "Cheese 3.0 beta": ("Cheese", "3.0 beta", ""),
    "Cheese 3.0 beta2": ("Cheese", "3.0 beta2", ""),
    "Cheese 3.0 beta3": ("Cheese", "3.0 beta3", ""),
    "Cheng4 0.36c" : ("Cheng", "4.36c", ""),
    "Cheng4 0.36c+" : ("Cheng", "4.36c+", ""),
    "Cheng4 0.39" : ("Cheng", "4.39", ""),
    "Crafty_25.2_CCRL 64-bit 4CPU": ("Crafty", "25.2 CCRL", "64-bit 4CPU"),
    "Ethereal TCEC S20 DivP (PEXT)": ("Ethereal", "TCEC S20 DivP (PEXT)", ""),
    "Ethereal TCEC S20 DivP": ("Ethereal", "TCEC S20 DivP", ""),
    "EtherealClassical 12.89": ("Ethereal", "12.89 Classical", ""),
    "Ethereal 12.89A_PRO_Cup_8": ("Ethereal", "12.89A PRO Cup 8", ""),
    "Ethereal 12.89B_PRO_FRC": ("Ethereal", "12.89B PRO FRC", ""),
    "Ethereal 12.89_PRO_Cup_8": ("Ethereal", "12.89 PRO Cup 8", ""),
    "Fritz in Bahrain": ("Fritz", "in Bahrain", ""),
    "Glaurung 2.2 JA": ("Glaurung", "2.2 JA", ""),
    "Glaurung_2.2_CCRL 64-bit_4CPU": ("Glaurung", "2.2 CCRL", "64-bit 4CPU"),
    "Gull_20170410_CCRL 64-bit 4CPU": ("Gull", "20170410 CCRL", "64-bit 4CPU"),
    "Igel 2.1.2 TCEC#3": ("Igel", "2.1.2 TCEC#3", ""),
    "Igel 2.1.2 next.2_TCEC_TTFIX": ("Igel", "2.1.2_next.2_TCEC_TTFIX", ""),
    "Igel 3.0.5 128GiB": ("Igel", "3.0.5", "128GiB"),
    "Igel 3.0.5 256GiB": ("Igel", "3.0.5", "256GiB"),
    "Koivisto2 4.41": ("Koivisto", "4.41", "2"),
    "KomodoDragon 2885.00_copy": ("KomodoDragon", "2885.00", "copy"),
    "KomodoDragon 3.1_copy": ("KomodoDragon", "3.1", "copy"),
    "Komodo_10_CCRL 64-bit_4CPU": ("Komodo", "10 CCRL", "64-bit 4CPU"),
    "Komodo_14_CCRL 64-bit_4CPU": ("Komodo", "14 CCRL", "64-bit 4CPU"),
    "LCZero 0.30-dag-bord-lf-se-2_784058_copy": ("LCZero", "0.30-dag-bord-lf-se-2_784058", "copy"),
    "LCZero 0.30-dag-pr1821_BT2-3250000_copy": ("LCZero", "0.30-dag-pr1821_BT2-3250000", "copy"),
    "LCZero 0.31-dag-e429eeb-BT3-2790000_copy": ("LCZero", "0.31-dag-e429eeb-BT3-2790000", "copy"),
    "LCZero 0.7 ID125": ("LCZero", "0.7_ID125", ""),
    "LCZero copy 0.27.0d+Tilps/dje-magic_JH.94-100": ("LCZero", "0.27.0d+Tilps/dje-magic_JH.94-100", "copy"),
    "LCZero half 0.30-dag-bord-lf_784968": ("LCZero", "half 0.30-dag-bord-lf_784968", ""),
    "LCZeroCPU3pct v0.25-n591215 blitz": ("LCZeroCPU_3pct", "v0.25-n591215 blitz", ""),
    "Laser 1.8 beta 256th": ("Laser", "1.8 beta", "256th"),
    "Laser 1.8 beta": ("Laser", "1.8 beta", ""),
    "Marvin 3.4.0 256th": ("Marvin", "3.4.0", "256th"),
    "Minic 3.07 128GiB": ("Minic", "3.07", "128GiB"),
    "Minic 3.07 64GiB": ("Minic", "3.07", "64GiB"),
    "MrBob 1.0.0_dev": ("Mr_Bob", "1.0.0_dev", ""),
    "Redfish 19070105": ("Stockfish", "19070105", "Redfish"),
    "Redfish 20191209": ("Stockfish", "20191209", "Redfish"),
    "RubiChess 2.2-dev 128GiB": ("RubiChess", "2.2-dev", "128GiB"),
    "RubiChessClassical 2.0.1": ("RubiChess", "2.0.1 Classical", ""),
    "Rybka 4 Exp-61": ("Rybka", "4 Exp-61", ""),
    "SFNNUE 20200704-StockFiNN-0.2": ("Stockfish", "20200704-StockFiNN-0.2", "SFNNUE"),
    "ScorpioNN 3.0.15.3_copy": ("ScorpioNN", "3.0.15.3", "copy"),
    "ScorpioNN 3.0.15.5_copy": ("ScorpioNN", "3.0.15.5", "copy"),
    "SimpleEval2 20200731r14": ("SimpleEval", "20200731r14", "2"),
    "Sjeng c't 2010": ("Sjeng", "c't 2010", ""),
    "SlowChess Blitz Classic 2.26 16GiB": ("SlowChess Blitz", "Classic 2.26", "16GiB"),
    "Stockfish copy 20210113": ("Stockfish", "20210113", "copy"),
    "Stockfish dev-20231105-442c294a_copy": ("Stockfish", "dev-20231105-442c294a", "copy"),
    "Stockfish dev-20240605-5688b188 interleave": ("Stockfish", "dev-20240605-5688b188", "interleave"),
    "Stockfish dev-20240605-5688b188 localalloc": ("Stockfish", "dev-20240605-5688b188", "localalloc"),
    "Stockfish dev-20240605-5688b188 none": ("Stockfish", "dev-20240605-5688b188", "none"),
    "Stockfish dev16_202208061357_copy": ("Stockfish", "dev16_202208061357", "copy"),
    "StockfishClassical 202007311012": ("Stockfish", "202007311012 Classical", ""),
    "StockfishClassical": ("Stockfish", "Classical", ""),
    "StockfishNNUE 20200704-StockFiNN-0.2": ("Stockfish", "20200704-StockFiNN-0.2", "StockfishNNUE"),
    "Stockfish_11_CCRL 64-bit_4CPU": ("Stockfish", "11 CCRL", "64-bit 4CPU"),
    "Stockfish_13_CCRL 64-bit_4CPU": ("Stockfish", "13 CCRL", "64-bit 4CPU"),
    "Stockfish_15_CCRL 64-bit_4CPU": ("Stockfish", "15 CCRL", "64-bit 4CPU"),
    "Stoofvlees IIb5": ("Stoofvlees II", "b5", ""),
    "Wasp 4.10 copy": ("Wasp", "4.10", "copy"),
    "Wasp TCEC S11": ("Wasp", "TCEC S11", ""),
    "Weiss 0.10-dev-20200525 1": ("Weiss", "0.10-dev-20200525", "1"),
    "Weiss 0.10-dev-20200525 2": ("Weiss", "0.10-dev-20200525", "2"),
    "Xiphos 0.6 256th": ("Xiphos", "0.6", "256th"),
    "Zappa Mexico II": ("Zappa", "Mexico II", ""),
}

# Player name substitutions are checked when 'exceptionalNames' didn't match.
playerNameSubstitutions = {
    # format: <original name> <new name>
    "Chess22k": "chess22k",
    "LCZero100n": "LCZero_100n",
    "LCZero10kn": "LCZero_10k",
    "LCZero10n": "LCZero_10n",
    "LCZero10pct": "LCZero_10pct",
    "LCZero1kn": "LCZero_1k",
    "LCZero1n": "LCZero_1n",
    "LCZero1pct": "LCZero_1pct",
    "LCZero30pct": "LCZero_30pct",
    "LCZero3pct": "LCZero_3pct",
    "LCZeroCPU10pct": "LCZeroCPU_10pct",
    "LCZeroCPU1pct": "LCZeroCPU_1pct",
    "LCZeroCPU30pct": "LCZeroCPU_30pct",
    "LCZeroCPU3pct": "LCZeroCPU_3pct",
    "Lc0": "LCZero",
    "Stockfish0.1pct": "Stockfish_0.1pct",
    "Stockfish0.3pct": "Stockfish_0.3pct",
    "Stockfish0_1pct": "Stockfish_0.1pct",
    "Stockfish100kn": "Stockfish_100k",
    "Stockfish10Mn": "Stockfish_10M",
    "Stockfish10kn": "Stockfish_10k",
    "Stockfish10pct": "Stockfish_10pct",
    "Stockfish1Mn": "Stockfish_1M",
    "Stockfish1kn": "Stockfish_1k",
    "Stockfish1pct": "Stockfish_1pct",
    "Stockfish1thread": "Stockfish_1thread",
    "Stockfish25pct": "Stockfish_25pct",
    "Stockfish3pct": "Stockfish_3pct",
    "StockfishDepth1": "Stockfish_d1",
    "StockfishDepth2": "Stockfish_d2",
    "StockfishDepth3": "Stockfish_d3",
    "StockfishDepth4": "Stockfish_d4",
    "Stockfishd1": "Stockfish_d1",
    "Weiss30pct": "Weiss_30pct",
    "lc0": "LCZero",
    "pirarucu": "Pirarucu",
    "rofChade30pct": "rofChade_30pct",
}


def addSwissTestStockfishVersions():
    for i in range(1, 43):
        exceptionalNames[f"{i:02}Stockfish 2021013116"] = (
            "Stockfish",
            "2021013116",
            f"{i:02}",
        )
        exceptionalNames[f"{i:02}StockfishClassical 202007311012"] = (
            "Stockfish",
            "202007311012 Classical",
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


def addFixedStockfish15():
    # change "Stockfish_15_100M" to "Stockfish_100M (15)" etc.
    for i in [1, 3, 10, 30, 100, 300]:
        for s in ["k", "M", "G"]:
            suffix = f"{i}{s}"
            name = "Stockfish_15_" + suffix
            newname = "Stockfish_" + suffix
            exceptionalNames[name] = (newname, "15", "")
    exceptionalNames["Stockfish_15_300M scaled_to_450Mnodes"] = (
        "Stockfish_300M",
        "15",
        "scaled to 450Mnodes",
    )
    exceptionalNames["Renamedfish_15_3M"] = ("Stockfish_3M", "15", "renamed")


def addSlowChessBlitzVersions():
    versions = [
        "2.41 avx",
        "2.5 avx",
        "2.54 avx",
        "2.7 avx",
        "2.75 avx",
        "2.8 avx",
        "2.82 avx",
        "2.83 avx2",
        "2.9 avx2",
        "Classic 2.25",
        "Classic 2.26",
    ]

    for v in versions:
        exceptionalNames[f"SlowChess Blitz {v}"] = ("SlowChess Blitz", v, "")


def addDeepSjengVersions():
    versions = ["3.6 a8", "3.6 a13", "3.6 a14", "3.6 a16", "3.6 a24", "3.6 a29", "3.6 a30", "3.6 a31"]

    for v in versions:
        exceptionalNames[f"DeepSjeng {v}"] = ("DeepSjeng", v, "")


# prints the triplet 't' as:
# t[0] (t[1]) [t[2]]   -- t[1] and t[2] printed out only if non-empty
def serializeNameVersionTriplet(t):
    return f"{t[0]}{'' if t[1] == '' else ' (' + t[1] + ')'}{'' if t[2] == '' else ' [' + t[2] + ']' }"


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
                playerName = m.group(1)
                playerVersion = m.group(2)

                if playerName in playerNameSubstitutions:
                    playerName = playerNameSubstitutions[playerName]

                nameVersionTriplet = (playerName, playerVersion, "")

            else:
                nameVersionTriplet = (player, "", "")

            print(f'[{playerTagMatch.group(1)} "{serializeNameVersionTriplet(nameVersionTriplet)}"]')

        else:
            print(line)


def listEngineNames():
    playerTagMatcher = re.compile(r'\[(White|Black) "([^"]*)"\]', re.ASCII)
    regularNameVersionMatcher = re.compile(r"(.*) ([^ ]+)", re.ASCII)

    names = dict()

    for line in sys.stdin:
        line = line.rstrip()  # let's skip the newline

        playerTagMatch = playerTagMatcher.fullmatch(line)
        if playerTagMatch:
            player = playerTagMatch.group(2)

            if player in exceptionalNames:
                nameVersionTriplet = exceptionalNames[player]

            elif regularNameVersionMatcher.fullmatch(player):
                m = regularNameVersionMatcher.fullmatch(player)
                playerName = m.group(1)
                playerVersion = m.group(2)

                if playerName in playerNameSubstitutions:
                    playerName = playerNameSubstitutions[playerName]

                nameVersionTriplet = (playerName, playerVersion, "")

            else:
                nameVersionTriplet = (player, "", "")

            if nameVersionTriplet not in names:
                names[nameVersionTriplet] = serializeNameVersionTriplet(nameVersionTriplet)

    for v in sorted(names.values()):
        print(v)


def addSubstitutions():
    addSwissTestStockfishVersions()
    addSufiTaggedEngines()
    addFixedStockfish15()
    addSlowChessBlitzVersions()
    addDeepSjengVersions()


def listSubstitutions():
    addSubstitutions()

    print("# Full name tag to triplet substitutions\n")
    exceptionalNamesList = []
    for k, v in sorted(exceptionalNames.items()):
        exceptionalNamesList.append([k] + list(v))
    print(tabulate(exceptionalNamesList, headers=["Original name", "Name", "Version", "Event special tag"]))

    print("\n\n# Name substitutions (matched only if full name tag did not match)\n")
    exceptionalNamesList = []
    for k, v in sorted(playerNameSubstitutions.items()):
        exceptionalNamesList.append([k, v])
    print(tabulate(exceptionalNamesList, headers=["Original name", "Name"]))


def main(argv):
    # version check -- this script was developed with Python 3.9
    if sys.version_info < (3, 9):
        warning(f"Python version {sys.version_info.major}.{sys.version_info.minor} is not at least 3.9!")

    if len(argv) > 0:
        if argv[0] == "--list-substitutions":
            listSubstitutions()

        elif argv[0] == "--list-engines":
            listEngineNames()

        else:
            print(
                """Usage: fix-engine-names.py [OPTION]...

Reads a PGN from stdin and outputs a PGN with adjusted engine names.

Options:
--help                  This help
--list-engines          Instead of producing a PGN output, list all unique
                        engine names after substitutions
--list-substitutions    Print out all name --> triplet substitutions
"""
            )

    else:
        addSubstitutions()
        fixEngineNames()


if __name__ == "__main__":
    main(sys.argv[1:])
