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
    "MrBob 1.0.0_dev": ("Mr_Bob", "1.0.0_dev", ""),
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
    "Chat": ("TCEC Chat", "", ""),
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
            "202007311012_Classical",
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
    exceptionalNames["Renamedfish_15_3M"] = (
        "Stockfish_3M",
        "15",
        "renamed",  # or "copy"
    )


def amendEngineNames(player):
    name, space, rest = player.partition(" ")
    # "Cheng 4 0.36c" will then be dealt with in fixVariousVersions() below
    name = name.replace("Cheng4", "Cheng 4")
    name = name.replace("Chess22k", "chess22k")
    name = re.sub(r"[lL]c0", "LCZero", name)
    # replace underscore with digital point
    name = name.replace("0_1pct", "0.1pct")
    # include an underscore before 0.1pct, 10pct, 30pct etc
    name = re.sub(r"([a-zA-Z])(\d+(\.\d+)?pct)", r"\1_\2", name)
    # rename kn to k
    name = re.sub(r"([0-9])kn", r"\1k", name)
    # rename Mn to M
    name = re.sub(r"([0-9])Mn", r"\1M", name)
    # include an underscore before 1n, 100k, 10M, 1G etc
    if name not in ["chess22k", "we4k"]:
        name = re.sub(r"([a-zA-Z])(\d+(\d+)?[nkMG])", r"\1_\2", name)
    name = name.replace("Stockfishd1", "Stockfish_d1")
    name = name.replace("StockfishDepth", "Stockfish_d")
    name = name.replace("Stockfish1thread", "Stockfish_1thread")
    return name + space + rest


def fixCopyTags(t):
    name, version, tag = t
    if name.endswith(" copy"):
        name, c, _ = name.rpartition(" copy")
        tag = "copy" if tag == "" else tag + "_copy"
    if version.endswith("_copy"):
        version, c, _ = version.rpartition("_copy")
        tag = "copy" if tag == "" else tag + "_copy"
    if version == "copy":
        version = ""
        tag = "copy" if tag == "" else tag + "_copy"
    return name, version, tag


def fixMemoryAndThreadTags(t):
    name, version, tag = t
    if version in ["64GiB", "128GiB", "256GiB", "256th"]:
        tag = version
        name, _, version = name.rpartition(" ")
    return name, version, tag


def fixVariousTags(t):
    name, version, tag = t
    if version in ["interleave", "localalloc", "none"]:
        tag = version
        name, _, version = name.rpartition(" ")
    return name, version, tag


def fixVariousVersions(t):
    name, version, tag = t
    if " " in name:
        n, _, v = name.partition(" ")
        if n in [
            "Antifish",
            "Cheng",
            "Cheese",
            "DeepSjeng",
            "Fritz",
            "Glaurung",
            "Igel",
            "Laser",
            "LCZero",
            "LCZeroCPU_3pct",
            "Rodent",
            "Sjeng",
            "Stoofvlees",
            "Wasp",
            "Zappa",
        ]:
            name = n
            version = v + " " + version
            version = version.replace(" ", "_")
    return name, version, tag


def serializeNameVersionTriplet(t):
    s1 = "" if t[1] == "" else f" ({t[1]})"
    s2 = "" if t[2] == "" else f" [{t[2]}]"
    return f"{t[0]}{s1}{s2}"


def fixEngineNames():
    playerTagMatcher = re.compile(r'\[(White|Black) "([^"]*)"\]', re.ASCII)

    regularNameVersionMatcher = re.compile(r"(.*) ([^ ]+)", re.ASCII)

    for line in sys.stdin:
        line = line.rstrip()  # let's skip the newline

        playerTagMatch = playerTagMatcher.fullmatch(line)
        if playerTagMatch:
            player = playerTagMatch.group(2)

            player = amendEngineNames(player)

            if player in exceptionalNames:
                nameVersionTriplet = exceptionalNames[player]

            elif regularNameVersionMatcher.fullmatch(player):
                m = regularNameVersionMatcher.fullmatch(player)
                nameVersionTriplet = (m.group(1), m.group(2), "")

            else:
                nameVersionTriplet = (player, "", "")

            nameVersionTriplet = fixCopyTags(nameVersionTriplet)
            nameVersionTriplet = fixMemoryAndThreadTags(nameVersionTriplet)
            nameVersionTriplet = fixVariousTags(nameVersionTriplet)
            nameVersionTriplet = fixVariousVersions(nameVersionTriplet)

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
    addFixedStockfish15()

    fixEngineNames()


if __name__ == "__main__":
    main(sys.argv[1:])
