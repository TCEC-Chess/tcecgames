#!/usr/bin/python3

import math
import os
import re

num_groups = 10
elo_list_file = 'swiss9-elo.txt'
prev_winner = 'Stockfish'

engines = [
    'Stockfish',
    'LCZero',
    'Obsidian',
    'Berserk',
    'KomodoDragon',
    'Ethereal',
    'PlentyChess',
    'Integral',
    'Caissa',
    'Stormphrax',
    'Ceres',
    'RubiChess',
    'Viridithas',
    'Seer',
    'rofChade',
    'Stoofvlees',
    'Booot',
    'Ginkgo',
    'Uralochka',
    'Velvet',
    'Igel',
    'Arasan',
    'BlackMarlin',
    'DeepSjeng',
    'Reckless',
    'ice4',
    'Quanticade',
    'Halogen',
    'Pawnocchio',
    'Clover',
    'Horsie',
    'Tarnished',
    'Heimdall',
    'Renegade',
    'Torch',
    'Sirius',
    'Minic',
    'Monty',
    'Winter',
    'Patricia',
    'Lynx',
    'c4ke',
    'ChessFighter',
    'Princhess',
]

def printSeedingParameters(engines, num_groups, elo_list_file):
    print("number of engines:", len(engines))
    print("number of groups: ", num_groups)
    print("Elo listing:      ", elo_list_file)

def loadEngineElos(elo_list_file):
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    eloFilePath = os.path.join(dname, elo_list_file)

    #                       Rank       Name    Elo        +          -          games      score       OppElo     draws
    pattern = re.compile(r'([0-9]+)\s+(\S+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)%\s+([0-9]+)\s+([0-9]+)%')

    eloMap = { }

    with open(eloFilePath) as f:
        for line in f:
            line = line.strip()
            m = pattern.fullmatch(line)
            if m:
                eloMap[m.group(2)] = int(m.group(3))

    return eloMap

# reorder engines by Elo
def reorderEnginesByElo(engines, eloMap, prevWinner):
    eloMap = eloMap.copy()
    eloMap[prevWinner] = 9999

    # order by Elo and engine name (descending)
    reorderedList = sorted(engines, reverse = True, key = lambda e : str(eloMap[e]) + e)

    return reorderedList

# engine list
def printEngineListForSeeding(engines, eloMap, prevWinner):
    for e in engines:
        prevWinnerTag = " PREVIOUS WINNER" if prevWinner == e else ""
        print(f"# {e} ({eloMap[e]}){prevWinnerTag}")

# assign engines to groups
def assignEnginesToGroups(engines, num_groups):
    groups = { }
    for a in range(0, num_groups):
        groups[a] = [ ]

    engine = 0
    for group in range(0, num_groups):
        group_size = math.ceil((len(engines) - engine) / (num_groups - group))
        for i in range(0, group_size):
            groups[group].append(engines[engine])
            engine = engine + 1

    return groups

# print seeding groups
def printSeedingGroups(num_engines, groups, eloMap, prevWinner):
    print("\n{| class=\"wikitable\"")
    print("|+Seeding groups")
    print('|-')

    for group in range(0, len(groups)):
        print(f"| '''Group {chr(65 + group)}'''")
    for row in range(0, math.ceil(num_engines/len(groups))):
        print('|-')
        for group in range(0, len(groups)):
            if (row * len(groups) + group) < num_engines:
                engine = groups[group][row]
                orderingTag = "PREV_WINNER" if engine == prevWinner else str(eloMap[engine])
                print(f"| {engine} ({orderingTag})")
            else:
                print('|')
    print('|-')
    print('|}')

# create seeding order
def printSeedingOrder(groups):
    print("\nSeeding order:")
    rank = 0
    seed = 1
    while seed <= len(engines):
        for group in range(0, len(groups)):
            print(f'# (' + chr(group + 65) + str(rank + 1) + ")  " + groups[group][rank])
            seed = seed + 1
            if seed > len(engines):
                break
        rank = rank + 1


if __name__ == "__main__":
    printSeedingParameters(engines, num_groups, elo_list_file)
    eloMap = loadEngineElos(elo_list_file)
    print()
    print("Engine list for seeding: (Initial, unsorted)")
    printEngineListForSeeding(engines, eloMap, prev_winner)
    print()
    print("Engine list for seeding:")
    engines = reorderEnginesByElo(engines, eloMap, prev_winner)
    printEngineListForSeeding(engines, eloMap, prev_winner)
    groups = assignEnginesToGroups(engines, num_groups)
    printSeedingGroups(len(engines), groups, eloMap, prev_winner)
    printSeedingOrder(groups)
