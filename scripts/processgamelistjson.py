#!/usr/bin/python3

import getopt
import json
import os.path
import re
import shutil
import sys
import urllib.request
import chess.pgn

# globals
verbose_output = False
dry_run = False
operating_mode = "ENUMERATE"
input_directory = None
master_directory = None

def help_and_exit():
    print('''Usage: process-gamelist-json.py [options] <gamelist.json>

Reads the TCEC game list json file and performs archive
maintenance. By default, the events are enumerated and classified to
stdout.

Options:
-h --help                    This help
-n --dry-run                 Dry run, don't write anything to the file system.
   --master-dir=<dir>        Master archive directory.
   --pgn-check               Check that all PGNs listed in gamelist.json exist.
   --sync-from-dir=<dir>     Add missing event PGNs to master-archive from
                             a directory.
   --sync-from-web           Add missing event PGNs to master-archive from
                             TCEC web site.
    --generate-makefile      Output a makefile for generating all derivatives
-v --verbose                 Enable verbose output
''')
    sys.exit(1)


def info(str):
    sys.stderr.write(f"{str}\n")

def verbose(str):
    if (verbose_output):
        sys.stderr.write(f"{str}\n")

def warning(str):
    sys.stderr.write(f"Warning: {str}\n")

def fatal(str, exitcode):
    sys.stderr.write(f"Fatal: {str} (exit={exitcode})\n")
    sys.exit(exitcode)

def sort_key_from_event(event):
    return event["dno"]

def classify_event(season, event_id, event_name):
    if season == "Bonus":
        return "BONUS"

    if "Cup" in season:
        return "CUP"

    if season.isdigit():
        if ("test" in event_id.lower()) or ("test" in event_name.lower()):
            return "TEST"

        if ("bonus" in event_id.lower()) or ("bonus" in event_name.lower()):
            return "BONUS"

        if "frc" in event_id.lower():
            return "FRC"

        # old style main event ids
        if re.fullmatch('s[0-9]{1,2}stage([0-9][a-z]|rapid)', event_id):
            return "MAIN"

        # the full variety of new style main event ids
        if re.fullmatch('s[0-9]{1,2}division([a-z]|[0-9]|sf|[0-9][a-z]|rapid|blitz|playoff|l[0-9]|ql|cpul1)',
                        event_id):
            return "MAIN"

        # special cases
        if event_id in ["s9rapid", "s15division4a4bplayoff", "s16divisionl1playoff", "s17divisionplayofffordivp"]:
            return "MAIN"

        if re.fullmatch('s[0-9]{1,2}stage([a-z]|[0-9])', event_id):
            return "MAIN"

        if re.fullmatch('swiss [0-9]+', event_name.lower()):
            return "SWISS"

        if (re.fullmatch('scup[0-9]+.*', event_id)):
            return "CUP"

        # if we get here, then everything that doesn't match above is bonus (up to S19)
        if int(season) <= 19:
            return "BONUS"

        if event_id == "s21divisionif":
            return "MAIN"

        if event_id in ["s21divisionseev", "s21divisioneval"]:
            return "BONUS"

    warning(f"Don't know how to classify Season '{season}', event id '{event_id}', event name '{event_name}'")
    return "MISC"

def sync_pgn(pgnfile):
    # first, check that we have the master archive set
    if master_directory is None:
        fatal("Master directory not set", 3)

    if not os.path.isdir(master_directory):
        fatal(f"Not a directory: '{master_directory}'", 4)

    output_file = f"{master_directory}/{pgnfile}"


    if operating_mode == "SYNC-FROM-DIR":
        # check if we already have the file
        if os.path.isfile(output_file):
            return

        input_file = f"{input_directory}/{pgnfile}"
        if not os.path.isfile(input_file):
            warning(f"Input file not '{input_file}' not found")
            return

        info(f"{input_file} --> {output_file}")
        if not dry_run:
            shutil.copyfile(input_file, output_file)

    if operating_mode == "SYNC-FROM-WEB":
        # check if we already have the file
        if os.path.isfile(output_file):
            return

        input_url = f"https://tcec-chess.com/archive/json/{pgnfile}"

        info(f"{input_url} --> {output_file}")

        try:
            with urllib.request.urlopen(input_url) as f:
                pgncontent = f.read()
                if not dry_run:
                    outfile = open(output_file, "wb")
                    outfile.write(pgncontent)
                    outfile.close()

                f.close()

        except urllib.error.HTTPError:
            warning(f"Cannot fetch {input_url}: {sys.exc_info()[0]}")

    if operating_mode == "PGN-CHECK":
        if os.path.isfile(output_file):
            if os.stat(output_file).st_size == 0:
                info(f"Empty file: {output_file}")
                return

            # check whether the output is unicode
            f = open(output_file, "rb")
            try:
                f.read().decode('utf-8')
            except UnicodeDecodeError:
                info(f"Not an UTF-8 file: {output_file}")

            f.close()

        else:
            info(f"Missing: {output_file}")

def normalize_cup_season(event_class, season, event_name):
    if (event_class == "CUP"):
        match = re.fullmatch('Cup[ _]([0-9]+)', season)

        if match is None:
            return (season, "Cup " + str(int(season) - 12))

        return (str(12 + int(match.group(1))), season)

    if (season == "Bonus"):
        match = re.fullmatch('S([0-9]+) (.*)', event_name)
        return (match.group(1), match.group(2))

    return (season, event_name)

class SeasonClass:
    def __init__(self, output_file, category_file_base):
        self.events = { }
        self.output_file = output_file
        self.category_file_base = category_file_base

class EventClass:
    def __init__(self, output_file, event_class):
        self.src_files = [ ]
        self.timestamp = None
        self.output_file = output_file
        self.event_class = event_class

class EventFile:
    def __init__(self, filename, timestamp, url):
        self.filename = filename
        self.timestamp = timestamp
        self.url = url

def read_pgn_timestamp(pgnfile):
    pgn = open(pgnfile, "r")
    first_game_headers = chess.pgn.read_headers(pgn)
    pgn.close()

    # do we have precise UTC datetime?
    if "GameStartTime" in first_game_headers:
        return first_game_headers["GameStartTime"]

    # ok, fall back to date tag
    return first_game_headers["Date"].replace(".", "-")

def add_event(make_defs, event_class, season, event_name, event_file, event_url):

    if not os.path.isfile(event_file):
        return

    season, event_name = normalize_cup_season(event_class, season, event_name)

    if not season in make_defs:
        seasonnum = int(season)
        make_defs[season] = SeasonClass(f"out/full/seasons/TCEC-S{seasonnum:02d}.pgn", \
                                        f"out/full/tournaments/TCEC-S{seasonnum:02d}")

    if not event_name in make_defs[season].events:
        seasonnum = int(season)
        make_defs[season].events[event_name] = \
            EventClass(f"out/full/events/TCEC-S{seasonnum:02d}-{event_name}.pgn".replace(" ", "-"),
                       event_class)

    duplicate_file = False
    for i in make_defs[season].events[event_name].src_files:
        if i.filename == event_file:
            duplicate_file = True

    if not duplicate_file:
        pgntimestamp = read_pgn_timestamp(event_file)
        make_defs[season].events[event_name].src_files.append(EventFile(event_file, pgntimestamp, event_url))

        if (make_defs[season].events[event_name].timestamp is None) or \
           (make_defs[season].events[event_name].timestamp > pgntimestamp):
            make_defs[season].events[event_name].timestamp = pgntimestamp

def timestamp_from_event(event):
    return event[1].timestamp

def timestamp_from_eventfile(eventfile):
    return eventfile.timestamp

def output_make_defs(make_defs):

    # dependencies for phony rules
    all_full_seasons = [ ]
    all_full_tournaments = [ ]
    all_full_events = [ ]

    # Season rules
    for season in make_defs:
        season_rule = f"{make_defs[season].output_file}:"
        all_full_seasons.append(f"{make_defs[season].output_file}")

        for event in sorted(make_defs[season].events.items(), key=timestamp_from_event):
            season_rule = season_rule + f" {event[1].output_file}"

        season_rule = season_rule + "\n\tmkdir -p out/full/seasons/ && cat $^ >$@\n"
        print(season_rule)
        print(season_rule.replace("/full/", "/compact/"))

    # Season/event class rules
    for season in make_defs:
        for category in ["MAIN", "CUP", "FRC", "SWISS", "BONUS", "TEST"]:

            no_events = True

            for event in sorted(make_defs[season].events.items(), key=timestamp_from_event):
                if event[1].event_class == category:
                    if no_events:
                        tournament_rule = f"{make_defs[season].category_file_base}-" + category.lower() + ".pgn:"
                        all_full_tournaments.append(f"{make_defs[season].category_file_base}-" + category.lower() + ".pgn")
                        no_events = False
                    tournament_rule = tournament_rule + f" {event[1].output_file}"

            if not no_events:
                tournament_rule = tournament_rule + "\n\tmkdir -p out/full/tournaments/ && cat $^ >$@\n"
                print(tournament_rule)
                print(tournament_rule.replace("/full/", "/compact/"))

    # Event rules
    for season in make_defs:
        for event in make_defs[season].events:
            print(f"{make_defs[season].events[event].output_file}: eco.pgn", end = "")
            all_full_events.append(f"{make_defs[season].events[event].output_file}")
            all_src_files = ""

            for src_file in sorted(make_defs[season].events[event].src_files, key=timestamp_from_eventfile):
                print(" " + src_file.filename, end = "")

            print(f" # {make_defs[season].events[event].event_class} / {make_defs[season].events[event].timestamp}", end = "\n")
            print("\tmkdir -p out/full/events/")

            outputOp = ">$@"

            for src_file in sorted(make_defs[season].events[event].src_files, key=timestamp_from_eventfile):
                print("\tpgn-extract -eeco.pgn -s -w50000 " + src_file.filename + " | awk -f scripts/pgn-extract-fix.awk | " + \
                      "awk -f scripts/site-tag-fix.awk -v urlprefix='https://tcec-chess.com/#" + src_file.url + "'" + outputOp)
                outputOp = ">>$@"
                print("\t@echo \"" + src_file.url + "\"")
            print()

    # phony rules
    print(".PHONY: all-full-seasons all-full-tournaments all-full-events")
    print(".PHONY: all-compact-seasons all-compact-tournaments all-compact-events")
    print()
    print("all-full-seasons: " + " \\\n\t".join(all_full_seasons))
    print()
    print("all-full-tournaments: " + " \\\n\t".join(all_full_tournaments))
    print()
    print("all-full-events: " + " \\\n\t".join(all_full_events))
    print()
    print("all-compact-seasons: " + (" \\\n\t".join(all_full_seasons)).replace("/full/", "/compact/"))
    print()
    print("all-compact-tournaments: " + (" \\\n\t".join(all_full_tournaments)).replace("/full/", "/compact/"))
    print()
    print("all-compact-events: " + (" \\\n\t".join(all_full_events)).replace("/full/", "/compact/"))
    print()

def gamelist_to_master_index(gamelist):

    if operating_mode == "GENERATE-MAKEFILE":
        make_defs = { }

    for season in gamelist["Seasons"]:
        verbose(f"Season '{season}'")

        for event in sorted(gamelist["Seasons"][season]["sub"], key=sort_key_from_event, reverse=True):
            event_id = event["id"]
            event_file_base = event["abb"]
            event_name = event["menu"]
            event_url = event["url"]

            # check whether we have everything we need
            if (event_id is None) or (event_file_base is None) or (event_name is None) or (event_url is None):
                continue

            # divider check
            if event_id.endswith("divider") or event_file_base.endswith("None"):
                continue

            # we'll ignore the current event
            if event_id == "current":
                continue

            event_class = classify_event(season, event_id, event_name)

            if operating_mode == "ENUMERATE":
                print(f"{event_id} {event_class} '{season}' {event_file_base}.pgn '{event_name}'")

            if operating_mode in ("SYNC-FROM-DIR", "SYNC-FROM-WEB", "PGN-CHECK"):
                sync_pgn(f"{event_file_base}.pgn")

            if operating_mode == "GENERATE-MAKEFILE":
                add_event(make_defs, event_class, season, event_name, "master-archive/" + event_file_base + ".pgn", event_url)


    if operating_mode == "GENERATE-MAKEFILE":
        output_make_defs(make_defs)

def main(argv):
    global verbose_output
    global dry_run
    global operating_mode
    global input_directory
    global master_directory

    inputfile = ''

    # version check -- this script was developed with Python 3.9
    if sys.version_info < (3, 9):
        warning(f"Python version {sys.version_info.major}.{sys.version_info.minor} is not at least 3.9!")

    try:
        opts, args = getopt.getopt(argv, "hvn",
                                   ["help", "verbose", "dry-run", "master-dir=", "pgn-check",
                                    "sync-from-dir=", "sync-from-web", "generate-makefile"])
        inputfile = args[0]
    except getopt.GetoptError:
        help_and_exit()
    except IndexError:
        help_and_exit()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help_and_exit()
        if opt in ("-v", "--verbose"):
            verbose_output = True
        if opt in ("-n", "--dry-run"):
            dry_run = True
        if opt == "--master-dir":
            master_directory = arg
        if opt == "--sync-from-dir":
            operating_mode = "SYNC-FROM-DIR"
            input_directory = arg
        if opt == "--pgn-check":
            operating_mode = "PGN-CHECK"
        if opt == "--sync-from-web":
            operating_mode = "SYNC-FROM-WEB"
        if opt == "--generate-makefile":
            operating_mode = "GENERATE-MAKEFILE"

    gamefile = open(inputfile, 'r')
    gamelist = json.load(gamefile)
    gamefile.close()
    gamelist_to_master_index(gamelist)
