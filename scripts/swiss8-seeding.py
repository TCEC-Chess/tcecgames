#!/usr/bin/python3

import math

num_groups = 10

engines = [
    'LCZero',
    'Stockfish',
    'Berserk',
    'Obsidian',
    'KomodoDragon',
    'Ethereal',
    'Caissa',
    'Seer',
    'Ceres',
    'RubiChess',
    'rofChade',
    'Viridithas',
    'Stoofvlees',
    'Revenge',
    'Igel',
    'Reckless',
    'Uralochka',
    'Horsie',
    'Velvet',
    'Ginkgo',
    'Stormphrax',
    'BlackMarlin',
    'Arasan',
    'Minic',
    'DeepSjeng',
    'Clover',
    'Plentychess',
    'Integral',
    'Altair',
    'Booot',
    'ice4',
    'STRO4K',
    'Starzix',
    'Renegade',
    'Tucano',
    'ScorpioNN',
    'Stash',
    'Weiss',
    'Texel',
    'Patricia',
    'Sirius',
    'ChessFighter',
    'Lynx',
    'Princhess',
]

num_engines = len(engines)
print("number of engines:", num_engines)
print("number of groups: ", num_groups)
print()

groups = { }

for a in range(0, num_groups):
    groups[a] = [ ]

# engine list
print("Engine list for seeding:")
for e in engines:
    print("# " + e)

# assign engines to groups
engine = 0
for group in range(0, num_groups):
    group_size = math.ceil((num_engines - engine) / (num_groups - group))
    for i in range(0, group_size):
        groups[group].append(engines[engine])
        engine = engine + 1

print("\n{| class=\"wikitable\"")
print("|+Seeding groups")
print('|-')
for group in range(0, num_groups):
    print(f"| '''Group {chr(65 + group)}'''")
for row in range(0, math.ceil(num_engines/num_groups)):
    print('|-')
    for group in range(0, num_groups):
        if (row * num_groups + group) < num_engines:
            print('| ' + groups[group][row])
        else:
            print('|')
print('|-')
print('|}')

# create seeding order
print("\nSeeding order:")
rank = 0
seed = 1
while seed <= num_engines:
    for group in range(0, num_groups):
        print(f'# (' + chr(group + 65) + str(rank + 1) + ")  " + groups[group][rank])
        seed = seed + 1
        if seed > num_engines:
            break
    rank = rank + 1
